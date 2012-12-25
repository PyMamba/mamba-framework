
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
Tests for mamba.web.response
"""

from twisted.web import http
from twisted.trial import unittest

from mamba.web import response


class ResponseTest(unittest.TestCase):

    def test_response_ok_code_is_200(self):
        result = response.Ok()
        self.assertEquals(result.code, http.OK)

    def test_response_bad_request_code_is_400(self):
        result = response.BadRequest()
        self.assertEquals(result.code, http.BAD_REQUEST)

    def test_response_not_found_code_is_404(self):
        result = response.NotFound('')
        self.assertEquals(result.code, http.NOT_FOUND)

    def test_response_conflict_code_is_409(self):
        result = response.Conflict('None', 'None')
        self.assertEquals(result.code, http.CONFLICT)

    def test_response_already_exists_code_is_409(self):
        result = response.AlreadyExists('None', 'None')
        self.assertEquals(result.code, http.CONFLICT)

    def test_response_already_exists_subclass_conflict(self):
        self.assertTrue(issubclass(response.AlreadyExists, response.Conflict))

    def test_internal_server_error_code_is_500(self):
        result = response.InternalServerError('')
        self.assertEquals(result.code, http.INTERNAL_SERVER_ERROR)

    def test_not_implemented_code_is_501(self):
        result = response.NotImplemented('/test')
        self.assertEquals(result.code, http.NOT_IMPLEMENTED)
