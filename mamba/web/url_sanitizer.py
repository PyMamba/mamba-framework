# -*- test-case-name: mamba.test.test_url_sanitizer -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
.. module:: url_sanitizer
    :platform: Unix, Windows
    :synopsys: Sanitize URLs for a correct use

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

import re


class UrlSanitizer(object):
    """
    Sanitize URLs for a correct use
    """

    def __init__(self):
        self._slash_finder = re.compile(r'//+')

    def sanitize_string(self, url):
        return self._slash_finder.sub(
            '/', '/{url}'.format(url=url)
        ).rstrip('/')

    def sanitize_container(self, urls):
        return self._slash_finder.sub(
            '/', '/{url}'.format(url='/'.join(urls))
        ).rstrip('/')
