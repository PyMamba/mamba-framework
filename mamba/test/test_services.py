
# Copyright (c) 2013 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
Tests for mamba.utils.heroku
"""

import os

from twisted.trial import unittest
from twisted.internet.defer import Deferred
from storm.twisted.testing import FakeThreadPool

from mamba.core.services import threadpool, herokuservice


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


class TestHerokuService(unittest.TestCase):

    def setUp(self):

        os.environ['PYTHONHOME'] = '/app/.heroku/python'

    def tearDown(self):
        del os.environ['PYTHONHOME']

    def test_start_service(self):

        service = herokuservice.HerokuService()
        service.allowed = True
        service.startService()
        self.assertTrue(service.running)
        service.stopService()

    def test_stop_service(self):

        service = herokuservice.HerokuService()
        service.allowed = True
        service.startService()
        self.assertTrue(service.running)
        service.stopService()
        self.assertFalse(service.running)

    def test_start_service_do_nothing_if_no_in_heroku(self):

        os.environ['PYTHONHOME'] = ''
        service = herokuservice.HerokuService()
        service.allowed = True
        service.startService()
        self.assertFalse(service.running)

    def test_start_service_do_nothing_if_not_force_heroku_awake_config(self):

        service = herokuservice.HerokuService()
        service.allowed = False
        service.startService()
        self.assertFalse(service.running)

    def test_stop_service_do_nothing_if_not_started(self):

        class FakeTask(object):

            called = False

            def stop(self, value):
                self.called = True

        service = herokuservice.HerokuService()
        service.allowed = True
        service.ping_task = FakeTask()
        service.stopService()
        self.assertFalse(service.ping_task.called)

    def test_start_runs_looping_call(self):

        service = herokuservice.HerokuService()
        service.allowed = True
        service.startService()
        self.assertTrue(service.ping_task.running)
        service.stopService()

    def test_stop_strops_looping_call(self):

        service = herokuservice.HerokuService()
        service.allowed = True
        service.startService()
        self.assertTrue(service.ping_task.running)
        service.stopService()
        self.assertFalse(service.ping_task.running)

    def test_ping_do_nothing_if_no_heroku_url_is_configured(self):

        service = herokuservice.HerokuService()
        self.assertNotIsInstance(service.ping(), Deferred)
