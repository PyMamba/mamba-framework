# -*- test-case-name: mamba.test.test_database -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: database
    :platform: Unix, Windows
    :synopsis: Storm ORM Database implementation for Mamba

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

from storm.zope.interfaces import IZStorm
from storm.zope.zstorm import global_zstorm
from twisted.python.threadpool import ThreadPool
from zope.component import provideUtility, getUtility

from mamba.utils import config


class Database(object):
    """
    Storm ORM database provider for Mamba.

    :param pool: the thrad pool for this database
    :type pool: :class:`twisted.python.threadpool.ThreadPool`
    """

    def __init__(self, pool=None):
        if pool is None:
            pool = ThreadPool(name='DatabasePool')

        self.pool = pool
        self.started = False

        provideUtility(global_zstorm, IZStorm)
        self.zstorm = getUtility(IZStorm)
        self.zstorm.set_default_uri('main', config.Database().uri)

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
