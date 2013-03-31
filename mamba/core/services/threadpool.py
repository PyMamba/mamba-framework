
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: threadpool
    :platform: Unix, Windows
    :synopsis: Just a ThreadPool

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

from twisted.application import service


class ThreadPoolService(service.Service):
    """Service to be started by twistd
    """

    def __init__(self, pool):
        self.pool = pool

    def startService(self):
        service.Service.startService(self)
        self.pool.start()

    def stopService(self):
        service.Service.stopService(self)
        self.pool.stop()


__all__ = ['ThreadPoolService']
