
# Copyright (c) 2013 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
Tests for mamba.utils.heroku
"""

from twisted.trial import unittest
from storm.twisted.testing import FakeThreadPool

from mamba.core.services import threadpool


class ThreadpoolMock(FakeThreadPool):

    def __init__(self):
        self.start_called = 0
        self.stop_called = 0

    def start(self):
        self.start_called += 1

    def stop(self):
        self.stop_called += 1


class TestThreadPoolService(unittest.TestCase):

    def test_start_sevice(self):

        service = threadpool.ThreadPoolService(ThreadpoolMock())
        self.assertEqual(service.pool.start_called, 0)
        self.assertFalse(service.running)
        service.startService()
        self.assertEqual(service.pool.start_called, 1)
        self.assertTrue(service.running)
        service.stopService()

    def test_stop_service(self):

        service = threadpool.ThreadPoolService(ThreadpoolMock())
        service.startService()
        self.assertEqual(service.pool.stop_called, 0)
        self.assertTrue(service.running)
        service.stopService()
        self.assertEqual(service.pool.stop_called, 1)
        self.assertFalse(service.running)
