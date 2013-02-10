# -*- test-case-name: mamba.http.test_headers -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
The Page object is the main web application entry point.
"""

import platform

from mamba._version import version


class Headers(object):
    """
    An object that build the Application page header and returns it
    as a well formated *XHTML/HTML* string.
    """

    _doc_types = {
        'html': {
            'html5': 'html',
            'strict': (
                'HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" '
                '"http://www.w3.org/TR/html4/strict.dtd"'
            ),
            'transitional': (
                'HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional'
                '//EN" "http://www.w3.org/TR/html4/loose.dtd"'
            ),
            'frameset': (
                'HTML PUBLIC "-//W3C//DTD HTML 4.01 Frameset//EN" '
                '"http://www.w3.org/TR/html4/frameset.dtd"'
            )
        },
        'xhtml': {
            'xhtml5': 'html',
            'strict': (
                'html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" '
                '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"'
            ),
            'transitional': (
                'html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional'
                '//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-'
                'transitional.dtd"'
            ),
            'frameset': (
                'html PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN" '
                '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd"'
            )
        }
    }

    content_type = 'text/html'
    description = 'No Description'
    language = 'en'
    favicon = 'favicon.ico'
    platform_debug = False

    def get_doc_type(self, doctype):
        """
        Translate a :class:`mamba.web.Page` docType options to a valid
        **DOCTYPE** Header string.

        :param doctype: the doctype key to get
        :type doctype: str
        :returns: A valid **DOCTYPE** Header string
        :return type: str
        """

        dtype = doctype.split('-')[0]
        dtd = doctype.split('-')[1]
        if dtype in self._doc_types:
            if dtd in self._doc_types[dtype]:
                return self._doc_types[dtype][dtd]

        return ''

    def set_doc_type(self, doctype, val):
        """Sets the doctype

        :param doctype: the doctype key to set
        :type doctype: str
        :param val: the value to set
        :type val: str
        """

        dtype = doctype.split('-')[0]
        dtd = doctype.split('-')[1]
        self._doc_types[dtype] = {dtd: val}

    def get_language_content(self):
        """Returns the Headers language"""

        return self.language

    def get_description_content(self):
        """Returns the Headers description"""
        return self.description

    def get_generator_content(self):
        """Returns the meta generator content"""

        return (
            'Mamba Web Application Framework version {}'.format(
                version.short())
        )

    def get_mamba_content(self):
        """Returns mamba specific meta content"""

        if self.platform_debug:
            return ('Platform: %s; Version: {};Arch: {}'.format(
                platform.system(), platform.release(), platform.machine())
            )
        else:
            return 'Platform: Web'

    def get_favicon_content(self, media='/media'):
        """Returns the favicon

        :param media: a media directory to add, defaults to `/media`
        :type media: str
        """

        return '{}/{}'.format(media, self.favicon)


__all__ = [
    "Headers"
]
