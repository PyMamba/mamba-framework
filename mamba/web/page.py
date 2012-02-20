# -*- test-case-name: mamba.test.test_web -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
The Page object is the main web application entry point.
"""

import os

from twisted.web import resource

from mamba._version import version
from mamba.http import headers


class Page(resource.Resource):
    """
    The Mamba Page object.
    
    @param options: The Mamba options for the Page content.
    """
    
    _options = {
        'doctype': 'html5',     # HTML5 by default
        'meta': []        
    }
    
    _header = headers.Headers()
    _resources_manager = None
    _controllers_manager = None
    _stylesheets = []
    _scripts = []
    
    
    def __init__(self, app):
        resource.Resource.__init__(self)
        
        self._options.update({
            'title': app.name,
            'description': app.description,
            'language': app.language           
        })
        
        # Set page language
        self._header.language = app.language
        # Set page description
        self._header.description = app.description
        # Set managers
        self._resources_manager = app.managers.get('resources')
        self._controllers_manager = app.managers.get('controllers')
        
    
    def getChild(self, path, request):
        """L{twisted.web.resource.Resource.getChild} overwrite"""
        
        if path == '' or path == None or path == 'index' or path == 'app':
            return self
        
        return resource.Resource.getChild(self, path, request)
    
    
    def render_GET(self, request):
        """Renders the index page"""
        
        _page = []
        a = _page.append
        
        # Create the page headers
        a('%s\n' % self._header.get_doc_type(self._options['doctype']))
        a('%s\n' % self._header.get_html_element())
        a('    <head>\n')
        a('        %s\n' % format(self._header.get_content_type()))
        a('        %s\n' % format(self._header.get_generator_content()))
        a('        %s\n' % format(self._header.get_description_content()))
        a('        %s\n' % format(self._header.get_language_content()))
        a('        %s\n' % format(self._header.get_mamba_content()))

        if 'resPath' in self._options and 'media' in self._options['resPath']:
            media=self._options['resPath']['media']
        else:
            media='media'
        a('        %s\n' % (self._header.get_favicon_content(media)))

        # Iterate over the defined meta keys and add it to the header's page
        for meta in self._options['meta']:
            a('        %s\n' % (meta))

        # Iterate over the defined styles and add it to the header's page
        for style in self._stylesheets:
            a('        %s\n' % (style.data))

        # Iterate over the defined scripts and add it to the header's page
        for script in self._scripts:
            a('        %s\n' % (script.data))

        a('        <title>%s</title>\n' % (self._options['title']))
        a('    </head>\n')
        a('</html>')

        # Return the rendered page
        return ''.join(_page)
    
    
    def add_meta(self, meta):
        """Adds a meta to the page header"""
        
        self._options['meta'].append(meta)
    
        
    def add_stylesheet(self, stylesheet):
        """Adds a stylesheet to the page"""
        
        self._stylesheets.append(stylesheet)
        self.putChild(stylesheet.prefix(), 
                      static.File(stylesheet.get_path()))
    
    
    def add_script(self, script):
        """Adds a script to the page"""
        
        self._scripts.append(script)
        self.putChild(script.get_prefix(), static.File(script.get_path()))
        
    