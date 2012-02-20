# -*- test-case-name: mamba.utils.test.test_camelcase -*- 
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

class CamelCase(object):
    """Stupid class that just offers stupid CamelCase funcionallity"""
    
    def __init__(self, camelize):
        self._camelized = None
        self._camelize = camelize
        super(CamelCase, self).__init__()                         
    
    def camelize(self, union=False):
        """Camelize and return camelized string"""
        
        if not union:
            joiner = ' '
        else:
            joiner = ''
        
        if type(self._camelize) is str:
            self._camelized = joiner.join(
                [p.capitalize() for p in self._camelize.split(' ')])
        elif type(self._camelize) is tuple or type(self._camelize) is list:
            self._camelized = joiner.join([
                p.capitalize() for p in self._camelize])
        elif type(self._camelize) is unicode:            
            self._camelized = joiner.join([
                p.capitalize() for p in self._camelize.split(' ')])
        else:
            raise ValueError('Expected str, tuple or list get %s instead.' % (
                type(self._camelize)))
        
        return self._camelized
