
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
.. module:: application
    :platform: Linux
    :synopsis: Objects for build Mamba Applications

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>
"""

from mamba.application.app import Application, _app_ver
from mamba.application.controller import (
    Controller, ControllerManager, ControllerProvider, ControllerError
)
from mamba.application.appstyles import AppStyles
from mamba.web.routing import Router

route = Router().route

__all__ = [
    'Application', '_app_ver',
    'Controller', 'ControllerManager', 'ControllerProvider', 'ControllerError',
    'AppStyles',
    'route'
]
