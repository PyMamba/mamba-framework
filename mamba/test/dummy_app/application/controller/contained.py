# -*- encoding: utf-8 -*-
# -*- mamba-file-type: mamba-controller -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>

"""
Test Dummy Container
"""

from zope.interface import implements

from mamba.web.response import Ok
from mamba.core import interfaces
from mamba.application import controller, route


class DummyContained(controller.Controller, controller.ControllerProvider):
    """
    I am a dummy controller to test Mamba
    """

    implements(interfaces.IController)
    name = 'DummyContained'
    desc = 'I am a dummy contained created for tests purposes'
    loaded = False
    __parent__ = 'container'
    __route__ = 'contained'

    def __init__(self):
        """
        Put here your initialization code
        """
        super(DummyContained, self).__init__()

    @route('/')
    def root(self, request):
        return Ok(
            '<!DOCTYPE html>'
            '   <html>'
            '       <head><title>Dummy Root</title></head>'
            '       <body>'
            '           <h1>This is the Dummy Contained Root. Fuck yeah!</h1>'
            '       </body>'
            '   </html>'
        )
