# -*- test-case-name: mamba.test.test_application -*- 
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

from mamba.web import stylesheet

class AppStyles(stylesheet.StylesheetManager):
	"""
	Manager for Application Stylesheets
	"""


	def __init__(self):
		"""
		Initialize
		"""

		self._styles_store = 'application/view/stylesheet'
		super(AppStyles, self).__init__()
	
	def get_styles(self):
		"""
		Return the pool
		"""

		return self.stylesheets


__all__ = [
	'AppStyles'
]