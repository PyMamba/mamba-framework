
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
Tests for mamba.application.app and mamba.scripts.mamba
"""

from twisted.trial import unittest
from twisted.web import resource
from twisted.internet.error import ProcessTerminated

from mamba import __version__
from mamba.plugin import ExtensionPoint
from mamba.core import interfaces, GNU_LINUX
from mamba.application import controller, app
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
        if GNU_LINUX:
            self.addCleanup(
                dcontroller._styles_manager.notifier.loseConnection
            )
            self.addCleanup(
                dcontroller._scripts_manager.notifier.loseConnection
            )

        self.assertTrue(interfaces.IController.providedBy(dcontroller))

    def test_dummy_controller_is_a_plugin(self):
        self.assertTrue(
            dummy.DummyController in controller.ControllerProvider.plugins)

    def test_get_client_ip_is_monkey_patched(self):
        mamba = app.Mamba()
        if GNU_LINUX:
            self.addCleanup(
                mamba.managers['controller'].notifier.loseConnection
            )
            self.addCleanup(mamba.managers['model'].notifier.loseConnection)

        from twisted.web.http import Request
        self.assertEqual(Request.getClientIP.__name__, 'getClientIPPatch')


if __name__ == '__main__':
    print('Use trial to run this tests: trial mamba.test.test_mamba')
