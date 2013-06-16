# -*- test-case-name: mamba.test.test_templating -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: templating
    :platform: Unix, Windows
    :synopsis: Templates Manager based on Jinja2 for Mamba

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

import os
from inspect import getframeinfo, currentframe, getfile

from jinja2 import Environment
from jinja2 import PackageLoader, FileSystemLoader, ChoiceLoader
from jinja2 import TemplateNotFound

from mamba.http import headers


class TemplateError(Exception):
    """Base class for Mamba Template related exceptions
    """


class NotConfigured(TemplateError):
    """Raised when we are missing configuration
    """


class MambaTemplate(object):
    """
    This class loads templates from the Mamba package and is used internally
    by Mamba. You are not supossed to use this class in your code

    :param env: jinja2 environment
    :type env: :class:`jinja2.Environment`
    :param template: the template to render
    :type template: str
    """

    def __init__(self, env=None, template=None):
        if env is None:
            loader = PackageLoader('mamba', 'templates/jinja')
            self.env = Environment(loader=loader)
        else:
            self.env = env

        self.template = template

    def render(self, **kwargs):
        """Renders a template
        """

        if self.template is None:
            raise NotConfigured(
                'Template is not configured. Missing template parameter at '
                'object construction time'
            )

        # if there is no template then we let it raise TemplateNotFound
        template = self.env.get_template(self.template)

        return template.render(**kwargs)


class Template(object):
    """
    This class loads and render templates from Mamba Applications view and
    controller directories.

    If controller is not None, then we use the controller directory templates
    instead of global view ones.

    :param env: the Jinja2 environment
    :param controller: mamba controller that uses the templates
    :type controller: :class:`~mamba.application.controller.Controller`
    :param cache_size: size of the Jinja2 templating environment
    :type cache: bool
    :raises: TemplateNotFound if no template is found in the filesystem
    :raises: NotConfigured it no parameters are provided
    """

    def __init__(self, env=None, controller=None, size=50, template=None):
        self.env = env
        self.loader = None
        self.cache_size = size
        self.template = template
        self.controller = controller
        self._header = headers.Headers()
        self.search_paths = [
            'application/view/templates',
            '{}/templates/jinja'.format(
                os.path.dirname(__file__).rsplit(os.sep, 1)[0]
            )
        ]

        if controller is not None:
            self.search_paths.append(
                'application/view/{}'.format(controller.name)
            )

            if 'application' not in controller.__module__:
                # this controller is a packed shared controller
                dum = controller.__module__.split('.', 1)[1].replace('.', '/')
                path = os.path.normpath('{}'.format(
                    getfile(controller.__class__).split(dum)[0]))
                self.search_paths.insert(
                    0, '{}/view/{}'.format(path, controller.name))
                self.search_paths.insert(0, '{}/view/templates'.format(path))
                self.loader = ChoiceLoader

    def render(self, template=None, **kwargs):
        """
        Renders a template and get the result back

        :param template: the template to render
        :type template: string
        """

        if template is None:
            template = self.template

        if self.env is None:
            if kwargs.get('loader', None) is None:
                if self.loader is None:
                    loader = FileSystemLoader(self.search_paths)
                elif self.loader is ChoiceLoader:
                    loader = self.loader(
                        [FileSystemLoader(path) for path in self.search_paths]
                    )
                else:
                    loader = self.loader(self.search_paths)
            else:
                loader = kwargs.get('loader')(self.search_paths)

            self.env = Environment(
                autoescape=lambda name: (
                    name.rsplit('.', 1)[1] == 'html'
                    if name is not None else False
                ),
                cache_size=self.cache_size,
                loader=loader
            )

        for arg, value in kwargs.iteritems():
            if hasattr(self.env, arg):
                setattr(self.env, arg, value)

        if template is not None:
            try:
                tpl = self.env.get_template(template)
            except TemplateNotFound:
                if self.controller is None:
                    raise
                try:
                    tpl = self.env.get_template(template)
                except TemplateNotFound:
                    raise TemplateNotFound('{} template not found'.format(
                        template)
                    )

            return tpl.render(**kwargs)

        if self.controller is not None:
            template = '{}.html'.format(
                getframeinfo(currentframe().f_back).function
            )

            for key, value in self.controller.render_keys.iteritems():
                kwargs[key] = value

            return self.env.get_template(template).render(**kwargs)

        raise NotConfigured(
            'Template is not configured. Missing controller parameter at '
            'object construction time or template argument on method call'
        )
