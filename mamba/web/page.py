# -*- test-case-name: mamba.test.test_web -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module: page
    :platform: Unix, Windows
    :synopsis: The Page object is the main web application entry point

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>
"""

from twisted.internet import reactor
from twisted.python import log, filepath
from twisted.python.logfile import DailyLogFile
from twisted.web import resource, static, server

from mamba.http import headers
from mamba.core.templating import MambaTemplate, Template, TemplateNotFound


class Page(resource.Resource):
    """
    This represents a full web page in mamba applications. It's usually
    the root page of your web site/application.

    :param app: The Mamba Application that implements this page
    :type app: :class:`~mamba.application.app.Application`
    """

    def __init__(self, app):
        resource.Resource.__init__(self)

        self._options = {
            'doctype': 'html-html5',     # HTML5 by default
            'meta': []
        }

        self._header = headers.Headers()
        self._resources_manager = None
        self._controllers_manager = None
        self._stylesheets = []
        self._scripts = []

        self._options.update({
            'title': app.name,
            'description': app.description,
            'language': app.language
        })

        # register log file if any
        if app.log_file is not None:
            log.startLogging(DailyLogFile.fromFullPath(app.log_file))

        # set page language
        self._header.language = app.language

        # set page description
        self._header.description = app.description

        # set managers
        self._styles_manager = app.managers.get('styles')
        self._scripts_manager = app.managers.get('scripts')
        self._controllers_manager = app.managers.get('controller')

        # prepare styles container
        self.styles_container = static.Data(
            'There is nothing for you here', 'text/css')
        self.putChild('styles', self.styles_container)

        # prepare scripts container
        self.scripts_container = static.Data(
            'There is nothing for you here', 'text/css')
        self.putChild('scripts', self.scripts_container)

        # register controllers
        self.register_controllers()

        # insert stylesheets
        self.insert_stylesheets()

        # insert scripts
        self.insert_scripts()

        # static data
        self.putChild('mamba', static.File(filepath.os.getcwd() + '/static'))

        # load root default template
        self.root_template = MambaTemplate(template='root_page.html')

    def getChild(self, path, request):
        """twisted.web.resource.Resource.getChild overwrite
        """

        if path == '' or path is None or path == 'index' or path == 'app':
            return self

        return resource.Resource.getChild(self, path, request)

    def render_GET(self, request):
        """Renders the index page
        """

        if 'resPath' in self._options and 'media' in self._options['resPath']:
            media = self._options['resPath']['media']
        else:
            media = 'mamba'

        options = {
            'doctype': self._header.get_doc_type(self._options['doctype']),
            'header': {
                'content_type': self._header.content_type,
                'generator_content': self._header.get_generator_content(),
                'description_content': self._header.get_description_content(),
                'language_content': self._header.get_language_content(),
                'mamba_content': self._header.get_mamba_content(),
                'media': self._header.get_favicon_content(media),
                'metas': self._options['meta'],
                'styles': [s.data for s in self._stylesheets],
                'title': self._options['title'],
                'scripts': self._scripts
            }
        }

        try:
            template = Template(template='index.html')
            return str(template.render_template(**options))
        except TemplateNotFound:
            pass

        template = MambaTemplate(template='root_page.html')
        return str(template.render(**options))

    def add_meta(self, meta):
        """Adds a meta to the page header
        """

        self._options['meta'].append(meta)

    def add_script(self, script):
        """Adds a script to the page
        """

        self._scripts.append(script)
        self.putChild(script.prefix, static.File(script.path))

    def register_controllers(self):
        """Add a child for each controller in the ControllerManager
        """

        for controller in self._controllers_manager.get_controllers().values():
            log.msg(
                'Registering controller {} with route {} {}({})'.format(
                    controller.get('object').name,
                    controller.get('object').get_register_path(),
                    controller.get('object').name,
                    controller.get('module')
                )
            )

            self.putChild(
                controller.get('object').get_register_path(),
                controller.get('object')
            )

    def insert_stylesheets(self):
        """Insert stylesheets to the HTML
        """

        for name, style in self._styles_manager.get_styles().iteritems():
            log.msg(
                'Inserting mamberized {} stylesheet into the main HTML page '
                'with path {} and prefix {}'.format(
                    name, style.path, style.prefix
                )
            )

            self.styles_container.putChild(name, static.File(style.path))
            self._stylesheets.append(style)

    def insert_scripts(self):
        """Insert scripts to the HTML
        """

        for name, script in self._scripts_manager.get_scripts().iteritems():
            log.msg(
                'Inserting mamberized {} script into the main HTML page with '
                'path {} and prefix {}'.format(
                    name, script.path, script.prefix
                )
            )

            self.scripts_container.putChild(name, static.File(script.path))
            self._scripts.append(script)

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
