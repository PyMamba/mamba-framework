
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
Tests for L{mamba.application.app}
"""

from twisted.trial import unittest
from twisted.python import filepath

from mamba.application import app

class ApplicationTests(unittest.TestCase):
    """Tests for L{mamba.application.app}"""
    
    def setUp(self):    
        self.app = app.Application()                
        self.addCleanup(self.app._managers.get('controller').notifier.loseConnection)
        self.addCleanup(self.app._managers.get('styles').notifier.loseConnection)
    
    
    def test_construct_overwrite_options(self):        
        name1 = self.app.name        
        app_tmp = app.Application({'name': 'Test'})        
        self.addCleanup(app_tmp._managers.get('controller').notifier.loseConnection)
        self.addCleanup(self.app._managers.get('styles').notifier.loseConnection)

        self.assertNotEqual(name1, app_tmp.name)
    
    
    def set_get_attribute(self, key, value):        
        setattr(self.app, key, value)        
        self.assertEqual(getattr(self.app, key), value)
                    
    
    def test_set_get_name(self):
        self.set_get_attribute('name', 'Some Name')
    
    
    def test_set_get_desc(self):
        self.set_get_attribute('desc', 'Some Desc')
    
    
    def test_set_get_port(self):
        self.set_get_attribute('port', 8080)        
    
    
    def test_not_numeric_port_raises_exception(self):
        self.failUnlessRaises(app.ApplicationError, 
            self.set_get_attribute, key='port', value='8080')
    
    def test_set_get_log_file(self):
        self.set_get_attribute('log', '/tmp/logfile.log')
    
    
    def test_set_log_file_raises_exception(self):
        self.failUnlessRaises(app.ApplicationError, self.set_get_attribute, 
            key='log_file', value='/dontexists/logfile.php')    
    
    
    def test_set_get_file_name(self):
        self.set_get_attribute('file', 'test.tac')
    
    
    def test_set_get_app_project_ver(self):
        from twisted.python import versions
        self.set_get_attribute('project_ver',
                                    versions.Version('Project', 2, 0, 0))        
    
    
    def test_set_app_project_ver_raises_when_non_twisted_version(self):        
        self.failUnlessRaises(app.ApplicationError, self.set_get_attribute,
            key='project_ver', value='2.0')
        
    
    def test_set_get_js_dir(self):
        self.set_get_attribute('js_dir', 'app')
    
    
    def test_set_get_language_works(self):
        self.set_get_attribute('language', 'ep')
        
    
    
    def test_get_app_ver(self):        
        self.assertEqual(app._app_ver.short(), self.app.ver)        
    
    
    def test_get_mamba_ver(self):
        from mamba import _version
        
        self.assertEqual(_version.version.short(), self.app.mamba_ver)        
    
    
#    def test_get_template_was_called(self):
#        self.spy.get_template('tac')
#        
#        assert_that_method(self.spy.get_template).was_called()
#    
#    def test_get_template_raises_error(self):
#        self.failUnlessRaises(app.ApplicationError, self.spy.get_template, (
#            'dontexists'
#        ))
#    
#    def test_get_template_works(self):
#        self.assertNotEqual(None, self.spy.get_template('tac'))
#    
#    def test_build_template_files(self):        
#        self.app.build_template_files() 
#        app_config = self.app.options.get('app_config', None)               
#        self.assertNotEqual(app_config, None)
#        self.assertNotEqual(self.app.get_template('tac'), None)
#        self.assertNotEqual(self.app.get_template('home'), None)

    