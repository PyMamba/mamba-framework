
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

from twisted.trial import unittest
from pyDoubles.framework import *

from mamba.http import headers


class HeadersTest(unittest.TestCase):
    """Test for L{mamba.http.headers}"""

    def setUp(self):
        self.spy = proxy_spy(headers.Headers())

    def test_get_doctype(self):
        self.assertEqual(
            self.spy.get_doc_type('html-html5'), '<!DOCTYPE html>')
        assert_that_method(self.spy.get_doc_type).was_called()
