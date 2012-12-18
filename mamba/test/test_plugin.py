# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
Tests for L{mamba.plugin}
"""

from twisted.trial import unittest

from mamba import plugin


class DummyProviderTest:
    """
    A Dummy Provider for test purposes
    """

    __metaclass__ = plugin.ExtensionPoint


class DumbTest(DummyProviderTest):
    """A dummy dumb class"""

    name = 'Dumb'

    def get_name(self):
        return self.name


class PluginTest(unittest.TestCase):
    """
    Tests for L{mamba.plugin}
    """

    def test_extension_points(self):
        for dummy in DummyProviderTest.plugins:
            self.assertEquals(dummy().get_name(), 'Dumb')
