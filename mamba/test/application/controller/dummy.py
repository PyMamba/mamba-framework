# -*- encoding: utf-8 -*-
# -*- mamba-file-type: mamba-controller -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>

"""
Test Dummy Controller
"""

import json

from zope.interface import implements

from mamba.application import controller

class DummyController(controller.ControllerProvider, controller.Controller):
	"""
	I am a dummy controller to test Mamba
	"""


	implements(controller.IController)
	name = 'Dummy'
	desc = 'I am a dummy controller created for tests purposes'
	loaded = False
	def __init__(self):
		"""
		Put here your initialization code
		"""
	
	def render_GET(self, request):
		"""Process GET Request."""

		return json.dumps({'success' : False, 'error' : 'Not implemented yet.'})

	def render_POST(self, request):
		"""Process POST Request."""

		return json.dumps({'success' : False, 'error' : 'Not implemented yet.'})

	
	def get_register_path(self, request, **kwargs):
		"""
		Return the controller register path for URL Rewritting
		"""

		return 'dummy'
