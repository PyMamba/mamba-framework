# -*- encoding: utf-8 -*-
# -*- mamba-file-type: mamba-controller -*-
# Copyright (c) 2013 Oscar Campos <oscar.campos@member.fsf.org>

"""
Test Dummy Shared Controller
"""

import json

from twisted.internet import defer
from zope.interface import implements

from mamba.web.response import Ok
from mamba.core import interfaces
from mamba.application import controller, route


class DummyController(controller.Controller, controller.ControllerProvider):
    """
    I am a dummy controller to test Mamba
    """

    implements(interfaces.IController)
    name = 'DummyShared'
    desc = 'I am a dummy controller created for tests purposes'
    loaded = False
    __route__ = 'dummy'

    def __init__(self):
        """
        Put here your initialization code
        """
        super(DummyController, self).__init__()

    def render_GET(self, request):
        """Process GET Request."""

        return json.dumps({'success': False, 'error': 'Not implemented yet.'})

    def render_POST(self, request):
        """Process POST Request."""

        return json.dumps({'success': False, 'error': 'Not implemented yet.'})

    @route('/dummy_test')
    def dummy_test(self, request):
        return Ok('<h1>Dummy Test</h1>', {'content-type': 'text/html'})

    @route('/')
    def root(self, request):
        return Ok(
            '<!DOCTYPE html>'
            '   <html>'
            '       <head><title>Dummy Root</title></head>'
            '       <body>'
            '           <h1>This is the Dummy Root. Fuck yeah!</h1>'
            '       </body>'
            '   </html>'
        )

    @route('/defer')
    @defer.inlineCallbacks
    def deferred(self, request, **kwargs):
        val1 = yield 'Hello '
        val2 = yield 'Defer!'
        defer.returnValue(val1 + val2)
