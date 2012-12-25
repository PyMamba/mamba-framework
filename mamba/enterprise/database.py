# -*- test-case-name: mamba.test.test_database -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: database
    :platform: Linux
    :synopsis: Database abstraction.

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

from twisted.python.threadpool import ThreadPool

from mamba import plugin
from mamba.utils import borg


class DatabaseManager(borg.Borg):
    """
    Database abstraction.

    :param pool: the thrad pool for this database
    :type pool: :class:`twisted.python.threadpool.ThreadPool`
    """

    def __init__(self, pool=None):
        if pool is None:
            pool = ThreadPool(name='DatabaseManagerPool')

        self.pool = pool
        self.started = False

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


class DatabaseProvider:
    """
    Mount point for database plugins.

    Database Plugins implementing this reference should implements the
    IDatabaseProvider interface
    """

    __metaclass__ = plugin.ExtensionPoint
