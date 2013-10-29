# -*- test-case-name: mamba.test.test_resource -*-
# Copyright (c) 2012 - 2013 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: resource
    :platform: Unix, Windows
    :synopsis: Resources and resources manager for Mamba

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""


from twisted.web import static
from twisted.web.resource import NoResource, Resource as TwistedResource

from mamba.http import headers
from mamba.utils.config import Application
from mamba.application import scripts, appstyles


class Resource(TwistedResource):
    """
    Mamba resources base class. A web accessible resource that add common
    properties for scripts in Mamba applications
    """

    _styles_manager = appstyles.AppStyles()
    _scripts_manager = scripts.AppScripts()

    def __init__(self):
        TwistedResource.__init__(self)

        config = Application()

        # headers and render keys for root_page and index templates
        header = headers.Headers()
        self.render_keys = {
            'doctype': header.get_doctype(),
            'header': {
                'title': config.name,
                'content_type': header.content_type,
                'generator_content': header.get_generator_content(),
                'description_content': header.get_description_content(),
                'language_content': header.get_language_content(),
                'mamba_content': header.get_mamba_content(),
                'media': header.get_favicon_content('assets'),
                'styles': self._styles_manager.get_styles().values(),
                'scripts': self._scripts_manager.get_scripts().values(),
                'lessjs': Application().lessjs
            }
        }


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
