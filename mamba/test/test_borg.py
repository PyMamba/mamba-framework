
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
Tests for :class: `~mamba.utils.borg`
"""

from twisted.trial import unittest

from mamba.utils import borg


class StubObjectBorg(borg.Borg):
    def set_name(self, name):
        self._name = name

    def get_name(self):
        return self._name


class StubObject(StubObjectBorg):
    def set_name(self, name):
        self._name = name

    def get_name(self):
        return self._name


class BorgTestCase(unittest.TestCase):

    def test_shared_information(self):
        item1 = StubObjectBorg()
        item1.set_name('Mamba')
        item2 = StubObjectBorg()

        self.assertEqual(item1.get_name(), item2.get_name())

    def test_not_shared_information_inheritance(self):
        item1 = StubObjectBorg()
        item1.set_name('Mamba')
        item2 = StubObject()
        item2.set_name('Python')
        item3 = StubObjectBorg()
        item4 = StubObject()

        self.assertEqual(item1.get_name(), item3.get_name())
        self.assertEqual(item2.get_name(), item4.get_name())
        self.assertNotEqual(item1.get_name(), item2.get_name())
