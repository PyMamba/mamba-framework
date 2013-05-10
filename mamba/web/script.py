# -*- test-case-name: mamba.test.test_web -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module: script
    :platform: Linux
    :synopsis: Mamba page script IResources

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>
"""

import re
from os.path import normpath

from mamba.core import GNU_LINUX

if GNU_LINUX:
    from zope.interface import implements
    from twisted.internet import inotify
    from twisted.python._inotify import INotifyError
    from mamba.core.interfaces import INotifier

from twisted.python import filepath

from mamba.utils import filevariables


class ScriptError(Exception):
    """Generic class for Script exceptions"""


class InvalidFileExtension(ScriptError):
    """Fired if the file has not a valid extension (.css or .less)"""


class InvalidFile(ScriptError):
    """Fired if a file is lacking the mamba css or less headers"""


class FileDontExists(ScriptError):
    """Raises if the file does not exists"""


class Script(object):
    """
    Object that represents an script

    :param path: the path of the script
    :type path: str
    :param prefix: the prefix where the script reside
    :type prefix: str
    """

    def __init__(self, path='', prefix='scripts'):
        self.path = path
        self.prefix = prefix
        self.name = ''
        self.data = ''
        self.type = ''

        self._fp = filepath.FilePath(self.path)
        if self._fp.exists():
            basename = filepath.basename(self.path)
            extension = filepath.splitext(basename)[1]
            if not basename.startswith('.') and (extension == '.js' or
                                                 extension == '.dart'):
                file_variables = filevariables.FileVariables(self.path)
                filetype = file_variables.get_value('mamba-file-type')
                if filetype != 'mamba-javascript' and filetype != 'mamba-dart':
                    raise InvalidFile(
                        'File {} is not a valid JavaScript '
                        'or Dart mamba file'.format(self.path)
                    )

                res = '{}/{}'.format(self.prefix, self._fp.basename())
                self.data = res
                self.name = self._fp.basename()
                self.type = ('text/javascript' if extension == '.js'
                             else 'text/dart')
            else:
                raise InvalidFileExtension(
                    'File {} has not a valid extension (.js or .dart)'.format(
                        self.path
                    )
                )
        else:
            raise FileDontExists(
                'File {} does not exists'.format(self.path)
            )


class ScriptManager(object):
    """
    Manager for Scripts
    """

    def __init__(self):
        self._scripts = {}

    @property
    def scripts(self):
        return self._scripts

    @scripts.setter
    def scripts(self, value):
        raise ScriptError("'scripts' is read-only")

    def setup(self):
        """
        Setup the loader and load the scripts
        """

        try:
            files = filepath.listdir(self._scripts_store)
            pattern = re.compile('[^_?]\%s$' % '.js|.dart', re.IGNORECASE)
            for stylefile in filter(pattern.search, files):
                stylefile = normpath(
                    '{}/{}'.format(self._scripts_store, stylefile)
                )
                self.load(stylefile)
        except OSError:
            pass

    def load(self, filename):
        """
        Load a new script file
        """

        style = Script(filename)
        self._scripts.update({style.name: style})

    def lookup(self, key):
        """
        Find and return a script from the pool
        """
        return self._scripts.get(key, None)


__all__ = ['ScriptError', 'Script', 'ScriptManager']
