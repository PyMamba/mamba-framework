# -*- test-case-name: mamba.test.test_web -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
.. module: stylesheet
    :platform: Linux
    :synopsis: Mamba page stylesheets IResources

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>
"""

import re

from zope.interface import implements
from twisted.internet import inotify
from twisted.python._inotify import INotifyError
from twisted.python import filepath

from mamba.core.interfaces import INotifier
from mamba.utils import filevariables


__all__ = ['StylesheetError', 'Stylesheet', 'StylesheetManager']


class StylesheetError(Exception):
    pass


class Stylesheet(object):
    """
    Object that represents an stylesheet or a less script
    """

    def __init__(self, path='', prefix='styles'):
        self.path = path
        self.prefix = prefix
        self.name = ''
        self.data = ''

        self._fp = filepath.FilePath(self.path)
        if self._fp.exists():
            basename = filepath.basename(self.path)
            extension = filepath.splitext(basename)[1]
            if not basename.startswith('.') and (extension == '.css' or
                                                 extension == '.less'):
                file_variables = filevariables.FileVariables(self.path)
                filetype = file_variables.get_value('mamba-file-type')
                if filetype != 'css' or filetype != 'less':
                    raise StylesheetError("%s" % (
                        "File %s is not a valid CSS or LESS file" % self.path
                    ))

                res = '%s/%s' % (self.prefix, self._fp.basename())
                self.data = '%s' % (
                    '<link rel="stylesheet" type="text/css" href="%s" />' % res
                )
                self.name = self._fp.basename()


class StylesheetManager(object):
    """
    Manager for Stylesheets
    """
    implements(INotifier)

    _stylesheets = dict()

    def __init__(self):
        # Create and setup Linux iNotify mechanism
        self.notifier = inotify.INotify()
        self.notifier.startReading()
        try:
            self.notifier.watch(
                filepath.FilePath(self._styles_store),
                callbacks=[self._notify]
            )
            self._watching = True
        except INotifyError:
            self._watching = False

    @property
    def stylesheets(self):
        return self._stylesheets

    @stylesheets.setter
    def stylesheets(self, value):
        raise StylesheetError("'stylesheets' is read-only")

    def setup(self):
        """
        Setup the loader and load the stylesheets
        """

        try:
            files = filepath.listdir(self._styles_store)
            pattern = re.compile('[^_?]\%s$' % '.css|.less', re.IGNORECASE)
            for file in filter(pattern.search, files):
                if self.is_valid_file(file):
                    self.load(file)
        except OSError:
            pass

    def load(self, filename):
        """
        Load a new stylesheet file
        """

        style = Stylesheet(filename, self._styles_store)
        self._stylesheets.update({style.name: style})

    def reload(self, style):
        """
        Reload a given script.

        This method just send a COMET / WebSocket petition to reload a
        specific CSS file.

        JavaScript to use:
            var queryString = '?reload=' + new Date().getTime();
            // ExtJS - Sencha
            var el = Ext.get(styleName);
            // LungoJS
            var el = $$(styleName);

            el.dom.href = el.dom.href.replace(/\?.*|$/, queryString);
        """

        # TODO: Make client to reload the CSS
        pass

    def lookup(self, key):
        """
        Find and return a stylesheet from the pool
        """
        return self._stylesheets.get(key, None)

    def is_valid_file(self, file_path):
        """Check if a file is a valid stylesheet file"""

        file_variables = filevariables.FileVariables(file_path)
        filetype = file_variables.get_value('mamba-file-type')
        return (filetype == 'css' or filetype == 'less')

    def _notify(self, wd, file_path, mask):
        """Notifies the changes on stylesheets file_path """

        if mask is inotify.IN_MODIFY:
            style = filepath.splitext(file_path.basename())[0]
            if style in self._stylesheets:
                self.reload(style)

        if mask is inotify.IN_CREATE:
            if file_path.exists():
                if self.is_valid_file(file_path):
                    self.load(file_path)
