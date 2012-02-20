# -*- test-case-name: mamba.core.test_inotifier -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
Mamba inotify related stuff
"""

from zope.interface import Interface, Attribute
from twisted.internet import inotify

class INotifier(Interface):
	"""
	Every Inotifier class will implement this interface
	"""


	def _notify(wd, file_path, mask):
		"""
		Notifies the chages on file_path filesystem directory
		The 'wd' param is ignored

		@param file_path: L{twisted.python.filepath.FilePath} on which the 
		event happened		
		@param mask: inotify event as hexadecimal mask
		"""
	
	notifier = Attribute("""
		@type notifier: C{twisted.internet.inotify.INotify}
		@ivar notifier: A notifier to start watching a FilePath
	""")


__all__ = [
	'INotifier'
]
	