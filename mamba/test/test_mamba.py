
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
Tests for L{mamba.application.app} and L{mamba.scripts.mamba}
"""

from zope.interface import implements
from zope.interface.verify import verifyObject

from twisted.web.test.test_web import DummyRequest
from twisted.python import filepath
from twisted.trial import unittest
from twisted.web import resource

from pyDoubles.framework import *
from pyDoubles.matchers import *

from mamba.test.application.controller import dummy
from mamba.application import controller
from mamba.plugin import ExtensionPoint
from mamba import __version__


class MambaTest(unittest.TestCase):
    
    
    def setUp(self):
        pass
    
    
    def test_get_version_is_string(self):
        self.assertIs(type(__version__), type(str()))
    
    
    def test_version_has_almost_major_and_minor(self):
        self.assertGreaterEqual(len(__version__.split('.')), 2)
    
    
    def test_version_is_12_03(self):
        self.assertEqual(__version__, '12.3.0')     
       
    
    def test_controller_provider(self):
    	self.assertTrue(controller.ControllerProvider, ExtensionPoint)
       
    
    def test_dummy_controller_inherits_resource(self):    	
    	self.assertTrue(issubclass(dummy.DummyController, resource.Resource))
    

    def test_dummy_controller_implements_icontroller(self):
    	self.assertTrue(controller.IController.implementedBy(
    		dummy.DummyController))
    

    def test_dummy_controller_instance_provide_icontroller(self):
    	dcontroller = dummy.DummyController()
    	self.assertTrue(controller.IController.providedBy(dcontroller))
    

    def test_dummy_controller_is_a_plugin(self):
        self.assertTrue(
            dummy.DummyController in controller.ControllerProvider.plugins)
    

    def test_dummy_controller_get_register_path(self):
        r = dummy.DummyController()         
        request = DummyRequest([''])
        request.args = {'action' : ['get_register_path']}
        request.prepath = []
        request.method = 'POST'
        self.assertEqual('dummy', r.render(request))
    

if __name__ == '__main__':
    print 'Use trial to run this tests: trial mamba.test.test_mamba'
    