# -*- test-case-name: mamba.test.test_templates -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: templates
    :platform: Unix, Windows
    :synopsis: Templates Manager based on Jinja2 for Mamba

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

from jinja2 import Environment, PackageLoader

env = Environment(loader=PackageLoader('mamba', 'templates/layout'))
