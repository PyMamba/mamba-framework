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


class DummyContainer(controller.Controller, controller.ControllerProvider):
    """
    I am a dummy controller to test Mamba
    """

    implements(interfaces.IController)
    name = 'DummyContainer'
    desc = 'I am a dummy container created for tests purposes'
    loaded = False
    __route__ = 'container'

    def __init__(self):
        """
        Put here your initialization code
        """
        super(DummyContainer, self).__init__()

    @route('/')
    def root(self, request):
        return Ok(
            '<!DOCTYPE html>'
            '   <html>'
            '       <head><title>Dummy Root</title></head>'
            '       <body>'
            '           <h1>This is the Dummy Container Root. Fuck yeah!</h1>'
            '       </body>'
            '   </html>'
        )
