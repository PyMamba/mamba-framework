# -*- test-case-name: mamba.test.test_database -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: database
    :platform: Unix, Windows
    :synopsis: Storm ORM Database implementation for Mamba

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

import datetime
import functools

from storm import properties
from storm.database import URI
from storm.expr import Undef, Column
from storm.zope.interfaces import IZStorm
from storm.zope.zstorm import global_zstorm
from storm.twisted.transact import Transactor
from twisted.python.monkey import MonkeyPatcher
from twisted.python.threadpool import ThreadPool
from zope.component import provideUtility, getUtility

from mamba import version
from mamba.utils import config
from mamba.enterprise.mysql import MySQL
from mamba.enterprise.sqlite import SQLite
from mamba.enterprise.common import CommonSQL
from mamba.enterprise.postgres import PostgreSQL
from twisted.internet.threads import deferToThreadPool


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
            zstorm = getUtility(IZStorm)
            zstorm.set_default_uri('mamba', config.Database().uri)

        SQLite.register()
        MySQL.register()
        PostgreSQL.register()

        # MonkeyPatch Storm
        if not self.monkey_patched:
            monkey_patcher = MonkeyPatcher(
                (properties, 'PropertyColumn', PropertyColumnMambaPatch),
                (Transactor, 'run', mamba_transactor_run)
            )
            monkey_patcher.patch()
            self.monkey_patched = True

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

    def store(self):
        """
        Returns a Store per-thread through :class:`storm.zope.zstorm.ZStorm`
        """

        if not self.started:
            self.start()

        zstorm = getUtility(IZStorm)
        return zstorm.get('mamba')

    def dump(self, model_manager, full=False):
        """
        Dumps the full database

        :param model_manager: the model manager from mamba application
        :type model_manager: :class:`~mamba.application.model.ModelManager`
        :param full: should be dumped full?
        :type full: bool
        """

        references = []
        sql = [
            '--',
            '-- Mamba SQL dump {}'.format(version.short()),
            '--',
            '-- Database Backend: {}'.format(self.backend),
            '-- Host: {}\tDatabase: {}'.format(self.host, self.database)
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
            sql.append('')
            for model in model_manager.get_models().values():
                if not model.get('object').on_schema():
                    continue
                if self.backend == 'postgres':
                    references.append(model.get('object').dump_references())

                sql += [model.get('object').dump_table() + '\n']
        else:
            for model in model_manager.get_models().values():
                model_object = model.get('object')

                if not model_object.on_schema():
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
                sql.append(model_object.dump_data())

                if self.backend == 'postgres':
                    references.append(model_object.dump_references())

        if self.backend == 'mysql':
            sql += [
                '--',
                '-- Enable foreign key checks',
                '--',
                'SET FOREIGN_KEY_CHECKS = 1;'
            ]

        for reference in references:
            sql.append(reference)

        return '\n'.join(sql)

    def reset(self, model_manager):
        """
        Delete all the data in the database and return it to primitive state

        :param model_manager: the model manager from mamba application
        :type model_manager: :class:`~mamba.application.model.ModelManager`
        """

        cfg = config.Database()
        cfg.create_table_behaviours['create_table_if_not_exists'] = False
        cfg.create_table_behaviours['drop_table'] = True

        sql = [
            model.get('object').dump_table()
            for model in model_manager.get_models().values()
            if model.get('object').on_schema() is True
        ]

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
        self.adapter_mapping = {
            'sqlite': SQLite, 'mysql': MySQL, 'postgres': PostgreSQL
        }

    def produce(self):
        return self.adapter_mapping.get(self.scheme, CommonSQL)(self.model)


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
        self.index = variable_kwargs.pop('index', False)
        self.unique = variable_kwargs.pop('unique', False)
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


def mamba_transactor_run(self, function, *args, **kwargs):
    """
    Monkeypatched version of the run method for storm transactor that
    can run the given function in a thread or in the main thread.

    If the named variable 'async' is set to False we don't run the
    function in the ThreadPool but in the main thread.
    """

    run_asynchornous = kwargs.pop('async', True)
    if run_asynchornous:
        # Inline the reactor import here for sake of safeness, in case a
        # custom reactor needs to be installed
        from twisted.internet import reactor
        return deferToThreadPool(
            reactor, self._threadpool, self._wrap, function, *args, **kwargs)

    return self._wrap(function, *args, **kwargs)


def transact(method):
    """Decorator that run the given method into the Transactor pool
    """

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        try:
            return self.transactor.run(method, self, *args, **kwargs)
        except AttributeError:
            return self.database.transactor.run(method, self, *args, **kwargs)
    return wrapper


__all__ = ['Database', 'AdapterFactory', 'transact']
