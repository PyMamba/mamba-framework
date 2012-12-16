
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
Tests for mamba.application.controller
"""

import sys
from collections import OrderedDict

from twisted.trial import unittest
from twisted.web import resource
from doublex import Spy, assert_that, is_, ANY_ARG, called

from mamba.web.response import Ok
from mamba.application import controller
from mamba.core.interfaces import INotifier


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

    def test_is_leaf(self):
        self.assertTrue(self.c.isLeaf)

    def test_send_back_works(self):

        def cb_assert_request(ignore, request):
            assert_that(request.registerProducer, called().times(1))
            assert_that(request.unregisterProducer, called())
            assert_that(request.write, called())

        with Spy() as request:
            request.registerProducer(ANY_ARG)
            request.unregisterProducer()
            request.write(ANY_ARG)
            request.setResponseCode(ANY_ARG)
            request.setHeader(ANY_ARG)

        result = Ok(
            {'name': 'Testing Environment'},
            {'content-type': 'application/json'}
        )

        d = self.c.sendback(result, request)
        d.addCallback(cb_assert_request, request)


class ControllerManagerTest(unittest.TestCase):
    """
    Tests for mamba.application.controller.ControllerManager
    """

    def setUp(self):
        self.mgr = controller.ControllerManager()
        self.addCleanup(self.mgr.notifier.loseConnection)

    def test_inotifier_provided_by_controller_manager(self):
        self.assertTrue(INotifier.providedBy(self.mgr))

    def test_get_controllers_is_ordered_dict(self):
        self.assertIsInstance(self.mgr.get_controllers(), OrderedDict)

    def test_get_controllers_is_empty(self):
        self.assertNot(self.mgr.get_controllers())

    def test_is_valid_file_works_on_valid(self):
        self.assertTrue(self.mgr.is_valid_file(
            '../mamba/test/application/controller/dummy.py'))

    def test_is_valid_file_works_on_invalid(self):
        self.assertFalse(self.mgr.is_valid_file('./test.log'))

    def test_is_loading_modules_and_lookup_works(self):
        sys.path.append('../mamba/test')
        self.mgr.load('../mamba/test/application/controller/dummy.py')
        self.assertTrue(self.mgr.length() != 0)
        dummy = self.mgr.lookup('dummy').get('object')
        self.assertTrue(dummy.name == 'Dummy')
        self.assertTrue('I am a dummy controller' in dummy.desc)
        self.assertTrue(dummy.loaded)
