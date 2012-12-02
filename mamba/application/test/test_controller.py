
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
Tests for L{mamba.application.controller}
"""

from twisted.trial import unittest
from twisted.web import resource

from mamba.application import controller


class ControllerTest(unittest.TestCase):
    """Tests for L{mamba.application.controller}"""

    def setUp(self):
        self.spy = resource.Resource()
        self.c = controller.Controller()

    def test_class_inherits_twisted_web_resource(self):
        self.assertTrue(issubclass(controller.Controller, resource.Resource))

    def test_is_not_leaf(self):
        self.assertFalse(self.c.isLeaf)
