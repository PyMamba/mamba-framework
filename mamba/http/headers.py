# -*- test-case-name: mamba.http.test_headers -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
The Page object is the main web application entry point.
"""

import platform

from mamba._version import version


class Headers(object):
    """
    An object that build the Application page header and returns it
    as a well formated XHTML/HTML string.    
    """
    _doc_types={
        'html'      : {
            'html5'         : '<!DOCTYPE html>',
            'strict'        : ('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML '
                '4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">'),
            'transitional'  : ('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 '
                'Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">'),
            'frameset'      : ('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 '
                'Frameset//EN" "http://www.w3.org/TR/html4/frameset.dtd">')
        },
        'xhtml'     : {
            'xhtml5'        : '<!DOCTYPE html>',
            'strict'        : ('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 '
                'Strict//EN" '
                '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'),
            'transitional'  : ('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 '
                'Transitional//EN" '
                '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'),
            'frameset'      : ('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 '
                'Frameset//EN" '
                '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd">')
        }
    }

    html_element= \
        '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">'
    content_type= \
        '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />'
    description='Non Description'
    language='en'
    favicon='favicon.ico'
    platform_debug = False

    def get_doc_type(self, doctype):
        """
        Translate a L{mamba.web.Page} docType options to a valid 
        DOCTYPE Header string.
        
        @return: A valid DOCTYPE Header string        
        """
        type=doctype.split('-')[0]
        dtd=doctype.split('-')[1]
        if type in self._doc_types:
            if dtd in self._doc_types[type]:
                return self._doc_types[type][dtd]

        return ''

    
    def set_doc_type(self, doctype, val):
        type=doctype.split('-')[0]
        dtd=doctype.split('-')[1]
        self._doc_types[type]={ dtd : val }

    
    def get_language_content(self):
        return '<meta name="language" content="%s" />' % self._language

    
    def get_description_content(self):
        return '<meta name="description" content="%s" />' % self._description

    
    def get_generator_content(self):        
        return ('<meta name="generator" '
            'content="Mamba Web Application Framework'
            ' version %s" />') % version.short()

    
    def get_mamba_content(self):
        if platform_debug:
            return ('<meta name="mamba-content" content="Platform: %s;'
                    'Version: %s;Arch: %s" />') % (
                    platform.system(), platform.release(), platform.machine())
        else:
            return '<meta name="mamba-content" content="Platform: Web" />'

    
    def get_favicon_content(self, media='/media'):
        return '<link rel="shortcut icon" href="%s/%s" />' % (
            media, self._favicon)


