# -*- test-case-name: mamba.test.test_response -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: response
    :platform: Unix, Windows
    :synopsys: Custom Response object for Mamba

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

import logging

from twisted.web import http
from twisted.python import log
from zope.interface import implementer

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


@implementer(IResponse)
class Ok(Response):
    """
    Ok 200 HTTP Response

    :param subject: the subject body of the response
    :type subject: :class:`~mamba.web.Response` or dict or str
    :param headers: the HTTP headers to return back in the response to the
                    browser
    :type headers: dict or a list of dicts
    """

    def __init__(self, subject='', headers={}):
        super(Ok, self).__init__(http.OK, subject, headers)


@implementer(IResponse)
class Created(Response):
    """
    Ok Created 201 HTTP Response

    :param subject: the subject body of the response
    :type subject: :class:`~mamba.web.Response` or dict or str
    :param headers: the HTTP headers to return back in the response to the
                    browser
    :type headers: dict or a list of dicts
    """

    def __init__(self, subject='', headers={}):
        super(Created, self).__init__(http.CREATED, subject, headers)


@implementer(IResponse)
class Unknown(Response):
    """
    Ok Unknown status 209 HTTP Response

    This HTTP code is not assigned, we will return this code when
    an enrouted method does not return anything to the browser
    """

    def __init__(self):
        super(Unknown, self).__init__(209, '', {})


@implementer(IResponse)
class MovedPermanently(Response):
    """
    Ok 301 Moved Permanently HTTP Response

    :param url: the url where the resource has been moved
    :type url: str

    .. seealso:: https://tools.ietf.org/html/rfc2616#page-62

    """

    def __init__(self, url):
        super(MovedPermanently, self).__init__(
            http.MOVED_PERMANENTLY,
            '',
            {
                'content-type': 'text/plain; charset=utf-8',
                'location': url
            }
        )


@implementer(IResponse)
class Found(Response):
    """
    Ok 302 Found HTTP Response

    :param url: the url where we want to redirect the browser
    :type url: str
    """

    def __init__(self, url):
        super(Found, self).__init__(
            http.FOUND,
            '',
            {
                'content-type': 'text/plain; charset=utf-8',
                'location': url
            }
        )


@implementer(IResponse)
class SeeOther(Response):
    """
    Ok 303 See Other HTTP Response

    :param url: the url where to find the information via GET
    :type url: str
    """

    def __init__(self, url):
        super(SeeOther, self).__init__(
            http.SEE_OTHER,
            '',
            {
                'content-type': 'text/plain; charset=utf8',
                'location': url
            }
        )


@implementer(IResponse)
class BadRequest(Response):
    """
    BadRequest 400 HTTP Response

    :param subject: the subject body of he response
    :type subject: :class:`~mamba.web.Response` or dict or str
    :param headers: the HTTP headers to return back in the response to the
                    browser
    :type headers: dict or a list of dicts
    """

    def __init__(self, subject='', headers={}):
        super(BadRequest, self).__init__(http.BAD_REQUEST, subject, headers)


@implementer(IResponse)
class Unauthorized(Response):
    """
    Unauthorized 401 HTTP Response
    """

    def __init__(self, subject='Unauthorized', headers={}):
        super(Unauthorized, self).__init__(http.UNAUTHORIZED, subject, headers)


@implementer(IResponse)
class NotFound(Response):
    """
    Error 404 Not Found HTTP Response

    :param subject: the subject body of he response
    :type subject: :class:`~mamba.web.Response` or dict or str
    :param headers: the HTTP headers to return back in the response to the
                    browser
    :type headers: dict or a list of dicts
    """

    def __init__(self, subject, headers={}):
        if not subject:
            subject = 'Mamba resource not found'

        super(NotFound, self).__init__(http.NOT_FOUND, subject, headers)


@implementer(IResponse)
class Conflict(Response):
    """
    Error 409 Conflict found

    :param subject: the subject body of he response
    :type subject: :class:`~mamba.web.Response` or dict or str
    :param value: the value of the conflicted operatio
    :param message: a customer user messahe for the response
    :type message: str
    """

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


@implementer(IResponse)
class AlreadyExists(Conflict):
    """
    Error 409 Conflict found in POST

    :param subject: the subject body of he response
    :type subject: :class:`~mamba.web.Response` or dict or str
    :param value: the value of the conflicted operatio
    :param message: a customer user messahe for the response
    :type message: str
    """

    def __init__(self, subject, value, message=''):
        super(AlreadyExists, self).__init__(
            subject,
            value,
            '{subject} already exists: {message}'.format(
                subject=subject,
                message=message
            )
        )


@implementer(IResponse)
class InternalServerError(Response):
    """
    Error 500 Internal Server Error

    :param message: a user custom message with a description of the nature
                    of the error
    :type message: str
    """

    def __init__(self, message):
        super(InternalServerError, self).__init__(
            http.INTERNAL_SERVER_ERROR,
            message,
            {'content-type': 'text/plain'}
        )


@implementer(IResponse)
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
