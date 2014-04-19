# -*- test-case-name: mamba.test.test_database -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: database
    :platform: Unix, Windows
    :synopsis: Storm ORM Database implementation for Mamba

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

import sys
import datetime
import functools
from sqlite3 import sqlite_version_info

if '__pypy__' in sys.modules:
    # try to use psycopg2ct if we are on PyPy
    try:
        from psycopg2ct import compat
        compat.register()

        # monkey patch to dont let Storm crash on register type
        import psycopg2
        psycopg2._psycopg = object

        class _psycopg:
            UNICODEARRAY = psycopg2.extensions.UNICODEARRAY

        from twisted.python.monkey import MonkeyPatcher
        monkey_patcher = MonkeyPatcher(
            (psycopg2, '_psycopg', _psycopg))
        monkey_patcher.patch()

    except ImportError:
        raise RuntimeError(
            'You are trying to use PostgreSQL with PyPy. Regular '
            'psycopg2 module don\'t work with PyPy, you may install '
            'psycopg2ct in order to can use psycopg2 with PyPy'
        )

from storm.database import URI
from storm.zope.interfaces import IZStorm
from storm.zope.zstorm import global_zstorm
from twisted.python.threadpool import ThreadPool
from zope.component import provideUtility, getUtility
from storm.twisted.transact import Transactor, DisconnectionError

from mamba import version
from mamba.utils import config
from mamba.enterprise.mysql import MySQL
from mamba.enterprise.sqlite import SQLite
from mamba.enterprise.common import CommonSQL
from mamba.enterprise.postgres import PostgreSQL


class Database(object):
    """
    Storm ORM database provider for Mamba.

    :param pool: the thrad pool for this database
    :type pool: :class:`twisted.python.threadpool.ThreadPool`
    """

    monkey_patched = False
    pool = ThreadPool(
        config.Database().min_threads,
        config.Database().max_threads,
        'DatabasePool'
    )
    zstorm_configured = False
    transactor = Transactor(pool)

    def __init__(self, pool=None, testing=False):
        if pool is not None:
            self.pool = pool
            self.transactor = Transactor(pool)

        self.started = False
        self.__testing = testing

        if not self.zstorm_configured:
            provideUtility(global_zstorm, IZStorm)
            self._patch_sqlite_uris()
            self._set_zstorm_default_uris(getUtility(IZStorm))

        SQLite.register()
        MySQL.register()
        PostgreSQL.register()

    @property
    def backend(self):
        """Return the type or types of backends this databse is using
        """

        return self._parse_uri('scheme')

    @property
    def host(self):
        """Return the hostname or hostnames this database is using
        """

        return self._parse_uri('host')

    @property
    def database(self):
        """Return the database name or names we are using
        """

        return self._parse_uri('database')

    def start(self):
        """Starts the Database (and the threadpool)
        """

        if self.started:
            return

        if self.__testing is True:
            self.pool.start()

        self.started = True

    def stop(self):
        """Stops the Database (and the threadpool)
        """

        if not self.started:
            return

        self.started = False

    def adjust_poolsize(self, min_threads=None, max_threads=None):
        """
        Adjusts the underlying threadpool size

        :param min: minimum number of threads
        :type min: int
        :param max: maximum number of threads
        :type max: int
        """

        self.pool.adjustPoolsize(min_threads, max_threads)

    def store(self, database='mamba', ensure_connect=False):
        """
        Returns a Store per-thread through :class:`storm.zope.zstorm.ZStorm`
        """

        if not self.started:
            self.start()

        if ensure_connect is True:
            self._ensure_connect()

        zstorm = getUtility(IZStorm)
        return zstorm.get(database)

    def dump(self, model_manager, scheme=None, full=False):
        """
        Dumps the full database

        :param model_manager: the model manager from mamba application
        :type model_manager: :class:`~mamba.application.model.ModelManager`
        :param scheme: dump which scheme? if None just everything
        :type scheme: str
        :param full: should be dumped full?
        :type full: bool
        """

        references = []
        indexes = []
        backend, host, database = self._parse_config_scheme(scheme)
        sql = [
            '--',
            '-- Mamba SQL dump {}'.format(version.short()),
            '--',
            '-- Database Backend: {}'.format(backend),
            '-- Host: {}\tDatabase: {}'.format(host, database)
        ]
        app = config.Application('config/application.json')
        try:
            sql += [
                '-- Application: {}'.format(app.name.decode('utf-8')),
                '-- Application Version: {}'.format(app.version),
                '-- Application Description: {}'.format(
                    app.description.encode('utf-8')
                )
            ]
        except AttributeError:
            pass

        sql += [
            '-- ---------------------------------------------------------',
            '-- Dumped on: {}'.format(datetime.datetime.now().isoformat()),
            '--'
        ]

        if self.backend == 'mysql':
            sql += [
                '-- Disable foreign key checks for table creation',
                '--',
                'SET FOREIGN_KEY_CHECKS = 0;'
            ]

        if full is False:
            self._dump_scheme(sql, references, indexes, model_manager, scheme)
        else:
            self._dump_data(sql, references, indexes, model_manager, scheme)

        if self.backend == 'mysql':
            sql += [
                '--',
                '-- Enable foreign key checks',
                '--',
                'SET FOREIGN_KEY_CHECKS = 1;'
            ]

        for reference in references:
            sql.append(reference)

        for index in indexes:
            sql.append(index)

        return '\n'.join(sql)

    def reset(self, model_manager, scheme=None):
        """
        Delete all the data in the database and return it to primitive state

        :param model_manager: the model manager from mamba application
        :type model_manager: :class:`~mamba.application.model.ModelManager`
        :param scheme: the specific scheme to reset (if any)
        :type scheme: str
        """

        sql = []
        for model in model_manager.get_models().values():
            if model.get('object').on_schema() is not True:
                continue

            if scheme is not None:
                if model.get('object').mamba_database() != scheme:
                    continue

            sql.append(
                model.get('object').drop_table(script=True, async=False))
            sql.append(model.get('object').dump_table())

        return '\n'.join(sql)

    def _parse_uri(self, parameter):
        """Parse the configured URI or URI's for the given parameter

        :param parameter: the parameter to extract from the URI
        :type parameter: str
        """

        results = []
        uri = config.Database().uri
        if type(uri) is dict:
            for key, value in uri.items():
                results.append({key: getattr(URI(value), parameter)})
        else:
            results = getattr(URI(uri), parameter)

        return results

    def _parse_config_scheme(self, scheme):
        """Take care of configuration scheme (if is not None)
        """

        if scheme is not None:
            host = [h[scheme] for h in self.host if scheme in h.keys()][0]
            db = [d[scheme] for d in self.database if scheme in d.keys()][0]
            back = [b[scheme] for b in self.backend if scheme in b.keys()][0]

            return back, host, db

        return self.backend, self.host, self.database

    def _dump_scheme(self, sql, references, indexes, model_manager, scheme):
        """Dump the database scheme
        """

        sql.append('')
        for model in model_manager.get_models().values():
            if not model.get('object').on_schema():
                continue

            if (scheme is not None
                    and model.get('object').mamba_database() != scheme):
                continue

            if self.backend == 'postgres':
                references.append(model.get('object').dump_references())

            if self.backend in ('postgres', 'sqlite'):
                if model.get('object').dump_indexes():
                    indexes.append(model.get('object').dump_indexes())

            sql += [model.get('object').dump_table() + '\n']

    def _dump_data(self, sql, references, indexes, model_manager, scheme):
        """Dump the database data
        """

        for model in model_manager.get_models().values():
            model_object = model.get('object')

            if not model_object.on_schema():
                continue

            if (scheme is not None
                    and model.get('object').mamba_database() != scheme):
                continue

            sql.append('--')
            sql.append('-- Table structure for table {}'.format(
                model_object.__storm_table__
            ))
            sql.append('--\n')
            sql.append(model_object.dump_table())
            sql.append('--')
            sql.append('-- Dumping data for table {}'.format(
                model_object.__storm_table__
            ))
            sql.append('--\n')
            sql.append(model_object.dump_data(scheme=scheme))

            if self.backend == 'postgres':
                references.append(model_object.dump_references())

            if self.backend in ('postgres', 'sqlite'):
                if model.get('object').dump_indexes():
                    indexes.append(model_object.dump_indexes())

    def _ensure_connect(self):
        """Ensure that we are connected to the database server
        """

        store = getUtility(IZStorm).get('mamba')
        try:
            store.execute('SELECT 1')
            store.commit()
        except DisconnectionError:
            store.rollback()

    def _set_zstorm_default_uris(self, zstorm):
        """Register the default_uri for each configured database with ZStorm
        """

        uri = config.Database().uri
        if type(uri) is dict:
            for database, real_uri in uri.items():
                zstorm.set_default_uri(database, real_uri)
        else:
            zstorm.set_default_uri('mamba', uri)

    def _patch_sqlite_uris(self):
        """Patch the URIs for SQLite configured databases
        """

        def patch(uri):
            """Closure to patch the URI
            """

            if uri.scheme == 'sqlite' and sqlite_version_info >= (3, 6, 19):
                if uri.options.setdefault('foreign_keys', '1') == '0':
                    uri.options['foreign_keys'] = '1'
                return str(uri)

        uri = config.Database().uri
        if type(uri) is dict:
            for database in uri:
                patched_uri = patch(URI(uri[database]))
                if patched_uri is not None:
                    config.Database().uri[database] = patched_uri
        else:
            patched_uri = patch(URI(uri))
            if patched_uri is not None:
                config.Database().uri = patched_uri


class AdapterFactory(object):
    """
    This is a factory which produces SQL Adapters.

    :param scheme: the database scheme (one of PostgreSQL, MySQL, SQLite)
    :type scheme: str
    :param model: the model to use with this adapter
    :type model: :class:`~mamba.Model`
    """

    def __init__(self, scheme, model):
        self.scheme = scheme
        self.model = model
        self.adapter_mapping = {
            'sqlite': SQLite, 'mysql': MySQL, 'postgres': PostgreSQL
        }

    def produce(self):
        return self.adapter_mapping.get(self.scheme, CommonSQL)(self.model)


def transact(method):
    """Decorator that run the given method into the Transactor pool
    """

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        kwargs['async'] = kwargs.pop(
            'async', getattr(self, '__mamba_async__', True))
        kwargs['auto_commit'] = kwargs.pop('auto_commit', True)
        try:
            return self.transactor.run(method, self, *args, **kwargs)
        except AttributeError:
            return self.database.transactor.run(method, self, *args, **kwargs)
    return wrapper


__all__ = ['Database', 'AdapterFactory', 'transact']
