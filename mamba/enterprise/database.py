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
        monkey_patcher = MonkeyPatcher((psycopg2, '_psycopg', _psycopg))
        monkey_patcher.patch()

    except ImportError:
        raise RuntimeError(
            'You are trying to use PostgreSQL with PyPy. Regular '
            'psycopg2 module don\'t work with PyPy, you may install '
            'psycoph2ct in order to can use psycopg2 with PyPy'
        )

from storm import properties
from storm.database import URI
from storm.expr import Undef, Column
from storm.zope.interfaces import IZStorm
from storm.zope.zstorm import global_zstorm
from twisted.python.monkey import MonkeyPatcher
from twisted.python.threadpool import ThreadPool
from zope.component import provideUtility, getUtility

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

    def __init__(self, pool=None):
        if pool is None:
            pool = ThreadPool(name='DatabasePool')

        self.pool = pool
        self.started = False

        provideUtility(global_zstorm, IZStorm)
        self.zstorm = getUtility(IZStorm)
        self.zstorm.set_default_uri('main', config.Database().uri)

        # register components
        SQLite.register()
        MySQL.register()
        PostgreSQL.register()

        # MonkeyPatch Storm
        if not self.monkey_patched:
            monkey_patcher = MonkeyPatcher(
                (properties, 'PropertyColumn', PropertyColumnMambaPatch)
            )
            monkey_patcher.patch()
            self.monkey_patched = True

    def start(self):
        """Starts the Database (and the threadpool)
        """

        if self.started:
            return

        self.pool.start()
        self.started = True

    def stop(self):
        """Stops the Database (and the threadpool)
        """

        if not self.started:
            return

        self.pool.stop()
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

    def store(self, model=None):
        """
        Returns a Store per-thread through :class:`storm.zope.zstorm.ZStorm`

        :param model: the registered per-model store, if None main store is
                      returned
        :type model: :class:`~mamba.application.model.Model`
        """

        if model is None or model.uri is None:
            return self.zstorm.get('main')

        return self.zstorm.get(model.__class__.__name__, model.uri)

    def dump(self, model_manager, full=False):
        """
        Dumps the full database

        :param model_manager: the model manager from mamba application
        :type model_manager: :class:`~mamba.application.model.ModelManager`
        :param full: should be dumped full?
        :type full: bool
        """

        app = config.Application('config/application.json')
        try:
            sql = [
                '--',
                '-- Mamba SQL dump {}'.format(version.short()),
                '--',
                '-- Database Backend: {}'.format(self.backend),
                '-- Host: {}\tDatabase: {}'.format(self.host, self.database),
                '-- Application: {}'.format(app.name),
                '-- Application Version: {}'.format(app.version),
                '-- Application Description: {}'.format(app.description),
                '-- ---------------------------------------------------------',
                '-- Dumped on: {}'.format(datetime.datetime.now().isoformat()),
                '--'
            ]
        except AttributeError:
            return 'error: \'config/application.json\' is missing... skipping'

        if full is False:
            sql.append('')
            sql += [
                model.get('object').dump_table()
                for model in model_manager.get_models().values()
            ]
        else:
            for model in model_manager.get_models().values():
                model_object = model.get('object')
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
                sql.append(model_object.dump_data())

        return '\n'.join(sql)

    @property
    def backend(self):
        """Return the type of backend this databse is using
        """

        return URI(config.Database().uri).scheme

    @property
    def host(self):
        """Return the hostname this database is using
        """

        return URI(config.Database().uri).host

    @property
    def database(self):
        """Return the database name we are using
        """

        return URI(config.Database().uri).database


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

    def produce(self):
        if self.scheme == 'sqlite':
            return SQLite(self.model)
        elif self.scheme == 'mysql':
            return MySQL(self.model)
        elif self.scheme == 'postgres':
            return PostgreSQL(self.model)
        else:
            return CommonSQL(self.model)


# Monkey Patching Storm (only a bit)
class PropertyColumnMambaPatch(Column):
    """
    We need to monkey patch part of Storm to can use size, unsigned
    and auto_increment named values in Properties.

    I'am supossed to work well with Storm since rev 223 (v0.12)
    """
    def __init__(self, prop, cls, attr, name, primary,
                 variable_class, variable_kwargs):
        # here we go!
        self.size = variable_kwargs.pop('size', Undef)
        self.unsigned = variable_kwargs.pop('unsigned', False)
        self.auto_increment = variable_kwargs.pop('auto_increment', False)
        self.array = variable_kwargs.pop('array', None)

        Column.__init__(self, name, cls, primary,
                        properties.VariableFactory(
                            variable_class, column=self,
                            validator_attribute=attr,
                            **variable_kwargs)
                        )

        self.cls = cls  # Used by references

        # Copy attributes from the property to avoid one additional
        # function call on each access.
        for attr in ["__get__", "__set__", "__delete__"]:
            setattr(self, attr, getattr(prop, attr))


__all__ = ['Database', 'AdapterFactory']
