# -*- test-case-name: mamba.test.test_templating -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: templating
    :platform: Unix, Windows
    :synopsis: Templates Manager based on Jinja2 for Mamba

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

from jinja2 import Environment, PackageLoader, TemplateNotFound


class TemplateError(Exception):
    """Base class for Template related exceptions
    """


class NotConfigured(TemplateError):
    """Raised when we don't have template or controller defined in the class
    """


class Template(object):
    """
    Just a small wrapper around Jinja2.

    If controller and template params are both given, controller has
    preference over template.

    :param env: jinja2 environment
    :type env: :class:`jinja2.Environment`
    :param template: the template to render
    :type template: str
    :param controller: the related controller
    :type controller: :class:`~mamba.application.controller.Controller`
    """

    def __init__(self, env=None, template=None, controller=None):
        if env is None:
            loader = PackageLoader('mamba', 'templates/layout')
            self.env = Environment(loader=loader)
        else:
            self.env = env

        self.template = template
        self.controller = controller

    def render(self):
        """Renders a template
        """

        if self.template is None and self.controller is None:
            raise NotConfigured(
                'Template is not configured (no termplate or controller has '
                'been passed to the constructor of the Template object)'
            )

        if self.controller is not None:
            return self._render_controller()

        if self.template is not None:
            return self._render_template()

    def _render_controller(self):
        """Renders a controller's template.
        """

