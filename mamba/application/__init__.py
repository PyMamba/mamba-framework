
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
.. module:: application
    :platform: Linux
    :synopsis: Objects for build Mamba Applications

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>
"""

from .app import Mamba, ApplicationError, _app_ver
from .controller import (
    Controller, ControllerManager, ControllerProvider, ControllerError
)
from .appstyles import AppStyles
from .model import Model, ModelManager
from mamba.web.routing import Router

route = Router().route

__all__ = [
    'Mamba', 'ApplicationError', '_app_ver',
    'Controller', 'ControllerManager', 'ControllerProvider', 'ControllerError',
    'AppStyles',
    'Model', 'ModelManager',
    'route'
]
