
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
Tests for L{mamba.utils.borg}
"""

from twisted.trial import unittest

from mamba.utils import borg

class StubObjectBorg(borg.Borg):    
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
