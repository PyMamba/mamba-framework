
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

from twisted.trial import unittest
from doublex import ProxySpy, assert_that, called, is_

from mamba.http import headers


class HeadersTest(unittest.TestCase):
    """Test for L{mamba.http.headers}"""

    def setUp(self):
        with ProxySpy(headers.Headers()) as spy:
            self.spy = spy

    def test_get_doctype(self):
        assert_that(
            self.spy.get_doc_type('html-html5'), is_('<!DOCTYPE html>'))
        assert_that(self.spy.get_doc_type, called().times(1))
