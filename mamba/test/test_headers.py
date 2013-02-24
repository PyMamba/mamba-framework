
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

from twisted.trial import unittest

from mamba.http import headers


class HeadersTest(unittest.TestCase):
    """Test for L{mamba.http.headers}"""

    def setUp(self):
        self.headers = headers.Headers()

    def test_get_doctype(self):
        self.assertEqual(self.headers.get_doctype(), 'html')
