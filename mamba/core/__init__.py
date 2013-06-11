
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

'''
Mamba core subpackage
'''

import sys

# we only support monitoring files on Linux. Maybe in the future we
# can implement a nice Twisted module like the inotify using kqueue
# in BSD/OS X and win32file/win32event in Windows
GNU_LINUX = True if 'linux' in sys.platform else False
BSD = True if 'bsd' in sys.platform else False
OSX = True if 'darwin' in sys.platform else False
WINDOWS = True if 'win' in sys.platform else False
POSIX = not WINDOWS

__all__ = ['GNU_LINUX', 'BSD', 'OSX', 'WINDOWS', 'POSIX']
