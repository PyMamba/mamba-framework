# -*- encoding: utf-8 -*-
# -*- mamba-file-type: mamba-controller -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>

"""
Test Dummy Controller
"""

import json

from zope.interface import implements
from twisted.internet import defer

from mamba.web.response import Ok
from mamba.core import interfaces
from mamba.application import controller, route


class DummyController(controller.Controller, controller.ControllerProvider):
    """
    I am a dummy controller to test Mamba
    """

    implements(interfaces.IController)
    name = 'Dummy'
    desc = 'I am a dummy controller created for tests purposes'
    loaded = False

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
    def dumm_test(self, request):
        return Ok('Dummy Test', {'content-type': 'plain/text'})
