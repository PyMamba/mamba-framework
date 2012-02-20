# -*- test-case-name: mamba.utils.test_less -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
Mamba less compiler
"""

import subprocess

from twisted.web import resource, server
from twisted.internet import threads
from twisted.python import filepath


class LessResource(resource.Resource):
	"""
	Mamba LessResource class define a web accesible LESS script
	"""

	isLeaf = True    
	def render_GET(self, request):
		"""
		Try to compile a LESS file and then serve it as CSS
		"""

		self.less_compiler = LessCompiler(request.postpath[0])		
		self.less_compiler.compile()
		
		return self.less_compiler.get_script()		


class LessCompiler(object):
	"""
	Compile LESS scripts if LESS NodeJS compiler is present. Otherwise adds the
	less.js JavaScript compiler at page.
	"""


	def __init__(self, style):
		super(LessCompiler, self).__init__()
		self.stylesheet = style		
			
	
	def compile(self):
		"""
		Compile a LESS script
		"""
		
		try:
			p = subprocess.Popen(['lessc', self.stylesheet],
				stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			self.out, errors = p.communicate()
		except OSError:
			from mamba.application import app
			mamba_app = app.Application()
			mamba_app.lessjs = True
			mgr = stylesheet.StylesheetManager()					
			self.out = filepath.FilePath(self.stylesheet).getContent()
	

	def get_script(self):
		"""
		Return the result script
		"""

		return self.out.decode('utf-8')
