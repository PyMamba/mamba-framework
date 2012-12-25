# -*- test-case-name: mamba.test.test_response -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
.. module:: response
    :platform: Unix, Windows
    :synopsys: Custom Response object for Mamba

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

import logging

from twisted.web import http
from twisted.python import log
from zope.interface import implements

from mamba.utils.output import brown
from mamba.core.interfaces import IResponse


class Response(object):
    """
    Mamba web request response base dummy object

    :param code: the HTML code for the response
    :type code: int
    :param subject: the subject body of he response
    :type subject: :class:`~mamba.web.Response` or dict or str
    :param headers: the HTTP headers to return back in the response to the
                    browser
    :type headers: dict or a list of dicts
    """

    def __init__(self, code, subject, headers):
        self.code = code
        self.subject = subject
        self.headers = headers

        if code in (http.BAD_REQUEST, http.NOT_FOUND):
            log.msg(brown(self.subject), logLevel=logging.WARN)
        elif code == http.OK:
            pass
        else:
            log.err(self)

    def __repr__(self):
        return 'IResponse({})'.format(
            ', '.join(map(repr, [self.code, self.subject, self.headers]))
        )


class Ok(Response):
    """
    Ok 200 HTTP Response

    :param subject: the subject body of he response
    :type subject: :class:`~mamba.web.Response` or dict or str
    :param headers: the HTTP headers to return back in the response to the
                    browser
    :type headers: dict or a list of dicts
    """

    implements(IResponse)

    def __init__(self, subject='', headers={}):
        super(Ok, self).__init__(http.OK, subject, headers)


class BadRequest(Response):
    """
    BadRequest 400 HTTP Response

    :param subject: the subject body of he response
    :type subject: :class:`~mamba.web.Response` or dict or str
    :param headers: the HTTP headers to return back in the response to the
                    browser
    :type headers: dict or a list of dicts
    """

    implements(IResponse)

    def __init__(self, subject='', headers={}):
        super(BadRequest, self).__init__(http.BAD_REQUEST, subject, headers)


class NotFound(Response):
    """
    Error 404 Not Found HTTP Response

    :param subject: the subject body of he response
    :type subject: :class:`~mamba.web.Response` or dict or str
    :param headers: the HTTP headers to return back in the response to the
                    browser
    :type headers: dict or a list of dicts
    """

    implements(IResponse)

    def __init__(self, subject, headers={}):
        if not subject:
            subject = 'Mamba resource not found'

        super(NotFound, self).__init__(http.NOT_FOUND, subject, headers)


class Conflict(Response):
    """
    Error 409 Conflict found

    :param subject: the subject body of he response
    :type subject: :class:`~mamba.web.Response` or dict or str
    :param value: the value of the conflicted operatio
    :param message: a customer user messahe for the response
    :type message: str
    """

    implements(IResponse)

    def __init__(self, subject, value, message=''):
        super(Conflict, self).__init__(
            http.CONFLICT,
            'Conflict for {subject} ({value}): {message}'.format(
                subject=subject,
                value=value,
                message=message
            ), {
                'x-mamba-subject': subject,
                'x-mamba-value': value
            }
        )


class AlreadyExists(Conflict):
    """
    Error 409 Conflict found in POST

    :param subject: the subject body of he response
    :type subject: :class:`~mamba.web.Response` or dict or str
    :param value: the value of the conflicted operatio
    :param message: a customer user messahe for the response
    :type message: str
    """

    implements(IResponse)

    def __init__(self, subject, value, message=''):
        super(AlreadyExists, self).__init__(
            subject,
            value,
            '{subject} already exists: {message}'.format(
                subject=subject,
                message=message
            )
        )


class InternalServerError(Response):
    """
    Error 500 Internal Server Error

    :param message: a user custom message with a description of the nature
                    of the error
    :type message: str
    """

    implements(IResponse)

    def __init__(self, message):
        super(InternalServerError, self).__init__(
            http.INTERNAL_SERVER_ERROR,
            message,
            {'content-type': 'text/plain'}
        )


class NotImplemented(Response):
    """
    Error 501 Not Implemented

    :param url: the URL that is not implemented
    :type url: str
    :param message: a user custom message describing the problem
    :type message: str
    """

    def __init__(self, url, message=''):
        super(NotImplemented, self).__init__(
            http.NOT_IMPLEMENTED,
            'Not Implemented: {url}\n{message}'.format(
                url=url, message=message
            ),
            {'content-type': 'text/plain'}
        )
