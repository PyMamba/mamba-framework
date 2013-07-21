
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
Tests for mamba.web.response
"""

from twisted.web import http
from twisted.trial import unittest

from mamba.web import response


class ResponseTest(unittest.TestCase):

    def test_response_ok_code_is_200(self):
        result = response.Ok()
        self.assertEqual(result.code, http.OK)

    def test_response_created_is_201(self):
        result = response.Created()
        self.assertEqual(result.code, http.CREATED)

    def test_response_moved_permanently_is_301(self):
        result = response.MovedPermaneently('none')
        self.assertEqual(result.code, http.MOVED_PERMANENTLY)

    def test_response_found_is_302(self):
        result = response.Found('none')
        self.assertEqual(result.code, http.FOUND)

    def test_see_other_is_303(self):
        result = response.SeeOther('none')
        self.assertEqual(result.code, http.SEE_OTHER)

    def test_response_bad_request_code_is_400(self):
        result = response.BadRequest()
        self.assertEqual(result.code, http.BAD_REQUEST)

    def test_response_unauthorized_code_is_401(self):
        result = response.Unauthorized()
        self.assertEqual(result.code, http.UNAUTHORIZED)

    def test_response_not_found_code_is_404(self):
        result = response.NotFound('')
        self.assertEqual(result.code, http.NOT_FOUND)

    def test_response_conflict_code_is_409(self):
        result = response.Conflict('None', 'None')
        self.assertEqual(result.code, http.CONFLICT)

    def test_response_already_exists_code_is_409(self):
        result = response.AlreadyExists('None', 'None')
        self.assertEqual(result.code, http.CONFLICT)

    def test_response_already_exists_subclass_conflict(self):
        self.assertTrue(issubclass(response.AlreadyExists, response.Conflict))

    def test_internal_server_error_code_is_500(self):
        result = response.InternalServerError('')
        self.assertEqual(result.code, http.INTERNAL_SERVER_ERROR)

    def test_not_implemented_code_is_501(self):
        result = response.NotImplemented('/test')
        self.assertEqual(result.code, http.NOT_IMPLEMENTED)
