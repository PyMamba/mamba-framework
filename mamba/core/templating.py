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
from inspect import getframeinfo, currentframe

from jinja2 import Environment, PackageLoader, FileSystemLoader
from jinja2 import TemplateNotFound


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

    If template argument is not

    :param controller: mamba controller that uses the templates
    :type controller: :class:`~mamba.application.controller.Controller`
    :param cache_size: size of the Jinja2 templating environment
    :type cache: bool
    :raises: TemplateNotFound if no template is found in the filesystem
    :raises: NotConfigured it no parameters are provided
    """

    def __init__(self, controller=None, cache_size=50, template=None, **kargs):
        self.controller = controller
        self.cache_size = cache_size
        self.template = template
        self.options = kargs

    def render_template(self, template=None, **kwargs):
        """
        Renders a template and get the result back

        :param template: the template to render
        :type template: string
        """

        if template is None:
            template = self.template

        env = Environment(
            autoescape=lambda name: (
                name.rsplit('.', 1)[1] == 'html' if name is not None else False
            ),
            cache_size=self.cache_size
        )

        for arg, value in self.options.iteritems():
            if hasattr(env, arg):
                setattr(env, arg, value)

        if template is not None:
            env.loader = FileSystemLoader([
                'application/view/templates',
                '{}/templates/jinja'.format(
                    os.path.dirname(__file__).rsplit('/', 1)[0]
                )
            ])
            try:
                tpl = env.get_template(template)
            except TemplateNotFound:
                if self.controller is None:
                    raise

                env.loader = FileSystemLoader([
                    'application/view/{}'.format(self.controller.name),
                    '{}/templates/jinja'.format(
                        os.path.dirname(__file__).rsplit('/', 1)[0]
                    )
                ])
                try:
                    tpl = env.get_template(template)
                except TemplateNotFound:
                    raise TemplateNotFound(
                        '{} template not found in `application/view/templates`'
                        ' or `application/view/{}`'.format(
                            template,
                            self.controller.name
                        )
                    )

            return tpl.render(**kwargs)

        if self.controller is not None:
            template = '{}.html'.format(
                getframeinfo(currentframe().f_back).function
            )

            env.loader = FileSystemLoader('application/view/{}'.format(
                self.controller.name)
            )

            return env.get_template(template).render(**kwargs)

        raise NotConfigured(
            'Template is not configured. Missing controller parameter at '
            'object construction time or template argument on method call'
        )
