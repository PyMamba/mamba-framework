# -*- test-case-name: mamba.test.test_web -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
.. module: stylesheet
    :platform: Unix, Windows
    :synopsis: The Page object is the main web application entry point

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>
"""

from twisted.python import log
from twisted.internet import reactor
from twisted.web import resource, static, server

from mamba.http import headers


class Page(resource.Resource):
    """
    This is the mamba root resource for Applications.

    :param options: The Mamba options for the Page content
    :type options: dict
    """

    _options = {
        'doctype': 'html-html5',     # HTML5 by default
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
        self._styles_manager = app.managers.get('style')
        self._controllers_manager = app.managers.get('controller')

        # register controllers
        self.register_controllers()

    def getChild(self, path, request):
        """L{twisted.web.resource.Resource.getChild} overwrite"""

        if path == '' or path is None or path == 'index' or path == 'app':
            return self

        return resource.Resource.getChild(self, path, request)

    def render_GET(self, request):
        """Renders the index page"""

        _page = []
        a = _page.append

        # Create the page headers
        a('{}\n'.format(self._header.get_doc_type(self._options['doctype'])))
        a('{}\n'.format(self._header.html_element))
        a('    <head>\n')
        a('        {}\n'.format(self._header.content_type))
        a('        {}\n'.format(self._header.get_generator_content()))
        a('        {}\n'.format(self._header.get_description_content()))
        a('        {}\n'.format(self._header.get_language_content()))
        a('        {}\n'.format(self._header.get_mamba_content()))

        if 'resPath' in self._options and 'media' in self._options['resPath']:
            media = self._options['resPath']['media']
        else:
            media = 'media'
        a('        {}\n'.format(self._header.get_favicon_content(media)))

        # Iterate over the defined meta keys and add it to the header's page
        for meta in self._options['meta']:
            a('        {}\n'.format(meta))

        # Iterate over the defined styles and add it to the header's page
        for style in self._stylesheets:
            a('        {}\n'.format(style.data))

        # Iterate over the defined scripts and add it to the header's page
        for script in self._scripts:
            a('        {}\n'.format(script.data))

        a('        <title>{}</title>\n'.format(self._options['title']))
        a('    </head>\n')
        a('</html>')

        # Return the rendered page
        return ''.join(_page)

    def add_meta(self, meta):
        """Adds a meta to the page header"""

        self._options['meta'].append(meta)

    def add_script(self, script):
        """Adds a script to the page"""

        self._scripts.append(script)
        self.putChild(script.get_prefix(), static.File(script.get_path()))

    def register_controllers(self):
        """Add a child for each controller in the ControllerManager"""

        for controller in self._controllers_manager.get_controllers().values():
            log.msg(
                'Registering controller {} with route {} {}({})'.format(
                    controller.get('object').name,
                    controller.get('object').__route__,
                    controller.get('object').name,
                    controller.get('module')
                )
            )

            self.putChild(
                controller.get('object').__route__,
                controller.get('object')
            )

    def run(self, port=8080):
        """
        Method to run the application within Twisted reactor

        This method exists for testing purposes only and fast
        controller test-development-test workflow. In production you
        should use twistd

        :param port: the port to listen
        :type port: number
        """
        factory = server.Site(self)
        reactor.listenTCP(port, factory)
        reactor.run()


__all__ = ['Page']
