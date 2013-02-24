# -*- test-case-name: mamba.http.test_headers -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
The Page object is the main web application entry point.
"""

import platform

from mamba._version import version
from mamba.utils.config import Application


config = Application()


class Headers(object):
    """
    An object that build the Application page header and returns it
    as a well formated *XHTML/HTML* string.
    """

    doctype = config.doctype
    content_type = config.content_type
    description = config.description
    language = config.language
    favicon = config.favicon
    platform_debug = config.platform_debug

    def get_doctype(self):
        """Get the configured or default mamba doctype (html by default)
        """

        return self.doctype

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
