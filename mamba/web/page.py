# -*- test-case-name: mamba.test.test_web -*-
# Copyright (c) 2012 - 2013 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module: page
    :platform: Unix, Windows
    :synopsis: The Page object is the main web application entry point

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>
"""

from singledispatch import singledispatch

from twisted.web import static, server
from twisted.python import log, filepath
from twisted.python.logfile import DailyLogFile

from mamba.utils.less import LessResource
from mamba.core import templating, resource

os = filepath.os


class Page(resource.Resource):
    """
    This represents a full web page in mamba applications. It's usually
    the root page of your web site/application.

    The controllers for the routing system are eregistered here. We first
    register any package shared controller because we want to overwrite
    them if our application defines the same routes.

    :param app: The Mamba Application that implements this page
    :type app: :class:`~mamba.application.app.Application`
    :param template_paths: additional template paths for resources
    :param cache_size: the cache size for Jinja2 Templating system
    :param loader: Jinja2 custom templating loader
    """

    def __init__(self, app, template_paths=None, cache_size=50, loader=None):
        resource.Resource.__init__(self)

        # register log file if any
        if (app.development is False and
                app.already_logging is False and app.log_file is not None):
            log.startLogging(DailyLogFile.fromFullPath(app.log_file))

        self._assets = resource.Assets([os.getcwd() + '/static'])
        self.template_paths = [
            'application/view/templates',
            '{}/templates/jinja'.format(
                os.path.dirname(__file__).rsplit(os.sep, 1)[0]
            )
        ]

        # set managers
        self._controllers_manager = app.managers.get('controller')
        self._shared_controllers_manager = app.managers.get('packages')

        # register controllers
        self.register_shared_controllers()
        self.register_controllers()

        # containers
        self.containers = {
            'styles': static.Data('', 'text/css'),
            'scripts': static.Data('', 'text/javascript')
        }
        # register containers
        self.putChild('styles', self.containers['styles'])
        self.putChild('scripts', self.containers['scripts'])
        # insert stylesheets and scripts
        self.insert_stylesheets()
        self.insert_scripts()

        # static accessible data (scripts, css, images, and others)
        self.putChild('assets', self._assets)

        # other initializations
        self.generate_dispatches()
        self.initialize_templating_system(template_paths, cache_size, loader)

    def getChild(self, path, request):
        """
        If path is an empty string or index, render_GET should be called,
        if not, we just look at the templates loaded from the view templates
        directory. If we find a template with the same name than the path
        then we render that template.

        .. caution::

            If there is a controller with the same path than the path
            parameter then it will be hidden and the template in templates
            path should be rendered instead

        :param path: the path
        :type path: str
        :param request: the Twisted request object
        """

        if path == '' or path is None or path == 'index':
            return self

        for template in self.environment.list_templates():
            if path == template.rsplit('.', 1)[0]:
                return self

        return resource.Resource.getChild(self, path, request)

    def render_GET(self, request):
        """Renders the index page or other templates of templates directory
        """

        if not request.prepath[0].endswith('.html'):
            request.prepath[0] += '.html'

        try:
            template = templating.Template(
                self.environment, template=request.prepath[0]
            )
            return template.render(**self.render_keys).encode('utf-8')
        except templating.TemplateNotFound:
            try:
                template = templating.Template(
                    self.environment, template='index.html'
                )
                return template.render(**self.render_keys).encode('utf-8')
            except templating.TemplateNotFound:
                pass

        template = templating.Template(
            self.environment,
            template='root_page.html'
        )
        return template.render(**self.render_keys).encode('utf-8')

    def generate_dispatches(self):
        """Generate singledispatches
        """

        self.add_template_paths = singledispatch(self.add_template_paths)
        self.add_template_paths.register(str, self._add_template_paths_str)
        self.add_template_paths.register(list, self._add_template_paths_list)
        self.add_template_paths.register(tuple, self._add_template_paths_tuple)

    def add_script(self, script):
        """Adds a script to the page
        """

        self.putChild(script.prefix, static.File(script.path))

    def register_controllers(self):
        """Add a child for each controller in the ControllerManager
        """

        for controller in self._controllers_manager.get_controllers().values():
            self._register_controller_module(controller)

    def register_shared_controllers(self):
        """
        Add a child for each shared package controller. If the package
        includes a static files directory we add an asset for it

        .. versionadded:: 0.3.6
        """

        if self._shared_controllers_manager is None:
            return

        for package in self._shared_controllers_manager.packages.values():
            static_data = filepath.FilePath(
                '{}/static'.format(os.path.normpath(package['path']))
            )
            if static_data.exists():
                self._assets.add_paths([static_data.path])

            real_manager = package.get('controller')
            if real_manager is None:
                continue

            for controller in real_manager.get_controllers().values():
                self._register_controller_module(controller, True)

    def initialize_templating_system(self, template_paths, cache_size, loader):
        """Initialize the Jinja2 templating system for static HTML resources
        """

        if self._shared_controllers_manager is not None:
            for package in self._shared_controllers_manager.packages.values():
                self.add_template_paths('{}/view/templates'.format(
                    package.get('path'))
                )

        if template_paths is not None:
            self.add_template_paths(template_paths)

        if loader is None:
            loader = templating.FileSystemLoader

        self.environment = templating.Environment(
            autoescape=lambda name: (
                name.rsplit('.', 1)[1] == 'html' if name is not None else False
            ),
            cache_size=cache_size,
            loader=loader(self.template_paths)
        )

    def insert_stylesheets(self):
        """Insert stylesheets into the HTML
        """

        for name, style in self._styles_manager.get_styles().iteritems():
            if style.less:
                self.containers['styles'].putChild(
                    name, LessResource(style.path)
                )
                continue

            self.containers['styles'].putChild(name, static.File(style.path))

    def insert_scripts(self):
        """Insert scripts to the HTML
        """

        for name, script in self._scripts_manager.get_scripts().iteritems():
            self.containers['scripts'].putChild(name, static.File(script.path))

    def run(self, port=8080):
        """
        Method to run the application within Twisted reactor

        This method exists for testing purposes only and fast
        controller test-development-test workflow. In production you
        should use twistd

        :param port: the port to listen
        :type port: number
        """
        from twisted.internet import reactor

        factory = server.Site(self)
        reactor.listenTCP(port, factory)
        reactor.run()

    def add_template_paths(self, paths):
        """Add template paths to the underlying Jinja2 templating system
        """

        raise RuntimeError(
            '{} type for paths can not be handled'.format(type(paths)))

    def _add_template_paths_str(self, paths):
        """Append template paths for single str template path given
        """

        self.template_paths.append(paths)

    def _add_template_paths_list(self, paths):
        """Adds the given template paths list
        """

        self.template_paths += paths

    def _add_template_paths_tuple(self, paths):
        """Adds the given template paths tuple
        """

        self.template_paths += list(paths)

    def _register_controller_module(self, controller, shared=False):
        """Efectively register the controller in the routing system

        :param controller: the controller to be registered
        :type controller: :class:`mamba.application.controller.Controller`
        :param shaed: is this a shared controller?
        :type shared: bool
        """

        log.msg(
            'Registering {} controller {} with route {} {}({})'.format(
                'shared' if shared else '',
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


__all__ = ['Page']
