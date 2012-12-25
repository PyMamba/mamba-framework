
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
Tests for mamba.web.url_sanitizer
"""

from twisted.trial import unittest

from mamba.web.url_sanitizer import UrlSanitizer


class UrlSanitizerTest(unittest.TestCase):

    def test_sanitize_string(self):
        self.assertEquals(
            UrlSanitizer().sanitize_string('//test////url///'),
            '/test/url'
        )

    def test_sanitize_container(self):
        self.assertEquals(
            UrlSanitizer().sanitize_container(['//test', '//url///']),
            '/test/url'
        )
