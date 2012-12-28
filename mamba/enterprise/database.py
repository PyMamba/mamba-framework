# -*- test-case-name: mamba.test.test_database -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: database
    :platform: Unix, Windows
    :synopsis: Storm ORM Database implementation for Mamba

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

from storm import properties
from storm.expr import Undef, Column
from storm.zope.interfaces import IZStorm
from storm.zope.zstorm import global_zstorm
from twisted.python.monkey import MonkeyPatcher
from twisted.python.threadpool import ThreadPool
from zope.component import provideUtility, getUtility

from mamba.utils import config
from mamba.enterprise.mysql import MySQL
from mamba.enterprise.sqlite import SQLite
from mamba.enterprise.dummy import DummySQL
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
        """Starts the Database (and the threadpool)"""

        if self.started:
            return

        self.pool.start()
        self.started = True

    def stop(self):
        """Stops the Database (and the threadpool)"""

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


class AdapterFactory(object):
    """
    This is a factory which produces SQL Adapters.

    :param scheme: the database scheme (one of PostgreSQL, MySQL, SQLite)
    :type scheme: str
    """

    def __init__(self, scheme, module):
        self.scheme = scheme
        self.module = module

    def produce(self):
        if self.scheme == 'sqlite':
            return SQLite(self.module)
        elif self.scheme == 'mysql':
            return MySQL(self.module)
        elif self.scheme == 'postgres':
            return PostgreSQL(self.module)
        else:
            return DummySQL(self.module)


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
