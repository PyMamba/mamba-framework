
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
Tests for L{mamba.utils.camelcase}
"""

from twisted.trial import unittest

from mamba.utils import camelcase

class TestCamelCase(unittest.TestCase):
    """Tests for L{mamba.utils.camelcase.CamelCase}"""
    
    def setUp(self):
        self.camel = camelcase.CamelCase('test case')
        self.camel_tuple = camelcase.CamelCase(('test', 'case'))
        self.camel_list = camelcase.CamelCase(('test', 'case'))
        self.camel_unicode = camelcase.CamelCase(u'test case')
    
    def test_camelcase(self):
        self.assertEquals(self.camel.camelize(), 'Test Case')                
    
    def test_camelcase_union(self):        
        self.assertEquals(self.camel.camelize(True), 'TestCase')
    
    def test_camelcase_tuple(self):        
        self.assertEquals(self.camel_tuple.camelize(), 'Test Case')
    
    def test_camelcase_tuple_union(self):        
        self.assertEquals(self.camel_tuple.camelize(True), 'TestCase')
    
    def test_camelcase_list(self):        
        self.assertEquals(self.camel_list.camelize(), 'Test Case')
    
    def test_camelcase_list_union(self):        
        self.assertEquals(self.camel_list.camelize(True), 'TestCase')
    
    def test_camelcase_unicode(self):
        self.assertEquals(self.camel_unicode.camelize(), u'Test Case')
    
    def test_camelcase_unknown_type_raises(self):
        camel = camelcase.CamelCase({'test':'case'})
        self.failUnlessRaises(ValueError, camel.camelize)
        