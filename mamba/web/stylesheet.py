# -*- test-case-name: mamba.test.test_web -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module: stylesheet
    :platform: Linux
    :synopsis: Mamba page stylesheets IResources

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>
"""

import re
from os.path import normpath

from twisted.python import filepath

from mamba.utils import filevariables


class StylesheetError(Exception):
    """Generic class for Stylesheet exceptions"""


class InvalidFileExtension(StylesheetError):
    """Fired if the file has not a valid extension (.css or .less)"""


class InvalidFile(StylesheetError):
    """Fired if a file is lacking the mamba css or less headers"""


class FileDontExists(StylesheetError):
    """Raises if the file does not exists"""


class Stylesheet(object):
    """
    Object that represents an stylesheet or a less script

    :param path: the path of the stylesheet
    :type path: str
    :param prefix: the prefix where the stylesheets reside
    :type prefix: str
    """

    def __init__(self, path='', prefix='styles'):
        self.path = path
        self.prefix = prefix
        self.name = ''
        self.data = ''
        self.less = False

        self._fp = filepath.FilePath(self.path)
        if self._fp.exists():
            basename = filepath.basename(self.path)
            extension = filepath.splitext(basename)[1]
            if not basename.startswith('.') and (extension == '.css' or
                                                 extension == '.less'):
                file_variables = filevariables.FileVariables(self.path)
                filetype = file_variables.get_value('mamba-file-type')
                if filetype != 'mamba-css' and filetype != 'mamba-less':
                    raise InvalidFile(
                        'File {} is not a valid CSS or LESS mamba file'.format(
                            self.path
                        )
                    )

                if filetype == 'mamba-less':
                    self.less = True

                res = '/{}/{}'.format(self.prefix, self._fp.basename())
                self.data = res
                self.name = self._fp.basename()
            else:
                raise InvalidFileExtension(
                    'File {} has not a valid extension (.css or .less)'.format(
                        self.path
                    )
                )
        else:
            raise FileDontExists(
                'File {} does not exists'.format(self.path)
            )


class StylesheetManager(object):
    """
    Manager for Stylesheets
    """

    def __init__(self, styles_store=None):
        self._stylesheets = {}
        if styles_store is not None:
            self._styles_store = styles_store

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
            for stylefile in filter(pattern.search, files):
                stylefile = normpath(
                    '{}/{}'.format(self._styles_store, stylefile)
                )
                self.load(stylefile)
        except OSError:
            pass

    def load(self, filename):
        """
        Load a new stylesheet file
        """

        style = Stylesheet(filename)
        self._stylesheets.update({style.name: style})

    def reload(self, style):
        """Send a COMET / WebSocket petition to reload a specific CSS file.

        :param style: the CSS file to reload
        :type style: :class:`~mamba.application.appstyle.AppStyle`

        JavaScript to use:

        .. sourcecode:: javascript

            var queryString = '?reload=' + new Date().getTime();
            // ExtJS - Sencha
            var el = Ext.get(styleName);
            // jQuery
            var el = $(styleName);
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


__all__ = ['StylesheetError', 'Stylesheet', 'StylesheetManager']
