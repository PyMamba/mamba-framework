
# Copyright (c) 2012 - 2013 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: resource
    :platform: Unix, Windows
    :synopsis: Resources and resources manager for Mamba

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

from singledispatch import singledispatch

from twisted.web import static
from twisted.python import filepath
from twisted.web.resource import NoResource, Resource as TwistedResource

from mamba.http import headers
from mamba.core import templating
from mamba.utils.config import Application
from mamba.application import scripts, appstyles


class Resource(TwistedResource):
    """
    Mamba resources base class. A web accessible resource that add common
    childs for scripts in Mamba applications

    :param template_paths: additional template paths for resources
    :param cache_size: the cache size for Jinja2 Templating system
    :param static: route for static data for this resouce
    """

    _styles_manager = appstyles.AppStyles()
    _scripts_manager = scripts.AppScripts()

    def __init__(self, template_paths=None, cache_size=50):
        TwistedResource.__init__(self)

        sep = filepath.os.sep
        self._templates = {}
        self.cache_size = cache_size
        self.template_paths = [
            'application/view/templates',
            '{}/templates/jinja'.format(
                filepath.os.path.dirname(__file__).rsplit(sep, 1)[0]
            )
        ]

        self.add_template_paths = singledispatch(self.add_template_paths)
        self.add_template_paths.register(str, self._add_template_paths_str)
        self.add_template_paths.register(list, self._add_template_paths_list)
        self.add_template_paths.register(tuple, self._add_template_paths_tuple)

        if template_paths is not None:
            self.add_template_paths(template_paths)

        self.config = Application()

        # headers and render keys for root_page and index templates
        header = headers.Headers()
        self.render_keys = {
            'doctype': header.get_doctype(),
            'header': {
                'title': self.config.name,
                'content_type': header.content_type,
                'generator_content': header.get_generator_content(),
                'description_content': header.get_description_content(),
                'language_content': header.get_language_content(),
                'mamba_content': header.get_mamba_content(),
                'media': header.get_favicon_content('assets'),
                'styles': self._styles_manager.get_styles().values(),
                'scripts': self._scripts_manager.get_scripts().values()
            }
        }

        # template environment
        self.environment = templating.Environment(
            autoescape=lambda name: (
                name.rsplit('.', 1)[1] == 'html' if name is not None else False
            ),
            cache_size=self.cache_size,
            loader=templating.FileSystemLoader(self.template_paths)
        )

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

        return TwistedResource.getChild(self, path, request)

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

        self.template_paths + paths

    def _add_template_paths_tuple(self, paths):
        """Adds the given template paths tuple
        """

        self.template_paths + list(paths)


class Assets(TwistedResource):
    """
    This object is used to serve the static assets for all the packages that
    we use in a mamba application.

    :param paths: a list of filepaths
    :type paths: list
    """

    def __init__(self, paths):
        TwistedResource.__init__(self)
        self.paths = []

        self.add_paths(paths)

    def add_paths(self, paths):
        """Add a new path to the list of paths

        :param path: the paths to add
        :type path: list
        """

        for path in paths:
            self.paths.append(static.File(path))

    def getChild(self, path, request):
        for file in self.paths:
            if path in file.listNames():
                return file.getChild(path, request)

        if path != '':
            return NoResource('File not found')

        return self

    def render_GET(self, request):
        return ''

    render_HEAD = render_GET
