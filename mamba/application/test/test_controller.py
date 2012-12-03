
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
Tests for mamba.application.controller
"""

import json
from collections import OrderedDict

from twisted.trial import unittest
from twisted.web import resource
from doublex import Spy, assert_that, is_, ANY_ARG, called

from mamba.application import controller


class ControllerTest(unittest.TestCase):
    """
    Tests for mamba.application.controller. I'm not goig to test the already
    well tested twisted.web.resource object here so those are really short
    and dumb tests.
    """

    def setUp(self):
        self.spy = resource.Resource()
        self.c = controller.Controller()

    def test_class_inherits_twisted_web_resource(self):
        self.assertTrue(issubclass(controller.Controller, resource.Resource))

    def test_is_not_leaf(self):
        self.assertFalse(self.c.isLeaf)

    def test_send_errback_works(self):
        with Spy() as request:
            request.finish()
            request.write(ANY_ARG)

        error = {
            'message': 'Test error message', 'number': '7327'
        }

        assert_that(self.c.senderrback(request, error), is_(None))
        assert_that(request.write, called().with_args(json.dumps({
            'success': False,
            'message': error['message'],
            'error': error['number']
        })).times(1))
        assert_that(request.finish, called().times(1))

    def test_send_back_works(self):
        with Spy() as request:
            request.registerProducer(ANY_ARG)
            request.unregisterProducer()
            request.write(ANY_ARG)

        result = {'message': 'Testing environment'}

        assert_that(self.c.sendback(request, result), is_(None))
        assert_that(request.registerProducer, called().times(1))
        # assert_that(request.unregisterProducer, called())
        # assert_that(request.write, called())


class ControllerManagerTest(unittest.TestCase):
    """
    Tests for mamba.application.controller.ControllerManager
    """

    def setUp(self):
        self.mgr = controller.ControllerManager()
        self.addCleanup(self.mgr.notifier.loseConnection)

    def test_get_controllers_is_ordered_dict(self):
        self.assertIsInstance(self.mgr.get_controllers(), OrderedDict)

    def test_get_controllers_is_empty(self):
        self.assertNot(self.mgr.get_controllers())

    def test_is_valid_file_works_on_valid(self):
        self.assertTrue(self.mgr.is_valid_file(
            '../mamba/test/application/controller/dummy.py'))

    def test_is_valid_file_works_on_invalid(self):
        self.assertFalse(self.mgr.is_valid_file('./test.log'))
