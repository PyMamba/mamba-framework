
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
Tests for mamba.application.app and mamba.scripts.mamba
"""

from twisted.trial import unittest
from twisted.web import resource

from mamba import __version__
from mamba.core import interfaces
from mamba.plugin import ExtensionPoint
from mamba.application import controller
from twisted.internet.error import ProcessTerminated
from mamba.test.dummy_app.application.controller import dummy


class MambaTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        self.flushLoggedErrors(ProcessTerminated)

    def test_get_version_is_string(self):
        self.assertIs(type(__version__), type(str()))

    def test_version_has_almost_major_and_minor(self):
        self.assertGreaterEqual(len(__version__.split('.')), 2)

    def test_version_is_correct(self):
        self.assertEqual(__version__, '0.1.0')

    def test_controller_provider(self):
        self.assertEqual(
            controller.ControllerProvider.__metaclass__.__name__,
            ExtensionPoint.__name__
        )

    def test_dummy_controller_inherits_resource(self):
        self.assertTrue(issubclass(dummy.DummyController, resource.Resource))

    def test_dummy_controller_implements_icontroller(self):
        self.assertTrue(interfaces.IController.implementedBy(
            dummy.DummyController))

    def test_dummy_controller_instance_provide_icontroller(self):
        dcontroller = dummy.DummyController()
        self.assertTrue(interfaces.IController.providedBy(dcontroller))

    def test_dummy_controller_is_a_plugin(self):
        self.assertTrue(
            dummy.DummyController in controller.ControllerProvider.plugins)


if __name__ == '__main__':
    print('Use trial to run this tests: trial mamba.test.test_mamba')
