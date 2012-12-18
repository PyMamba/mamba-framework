
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
Tests for mamba.web
"""

from cStringIO import StringIO

from twisted.trial import unittest
from twisted.internet import defer
from twisted.web.server import Request
from twisted.web.http_headers import Headers
from twisted.web.test.test_web import DummyRequest
from doublex import Stub, ProxySpy, Spy, called, assert_that

from mamba.application import route as decoroute
from mamba.web import stylesheet, page, asyncjson, response
from mamba.web.routing import Route, Router, RouteDispatcher
from mamba.test.application.controller.dummy import DummyController


class StylesheetTest(unittest.TestCase):

    def setUp(self):
        pass


class AsyncJSONTest(unittest.TestCase):

    @defer.inlineCallbacks
    def test_asyncjson(self):

        consumer = Spy(Request)

        ajson = ProxySpy(asyncjson.AsyncJSON({'id': 1, 'name': 'Test'}))
        r = yield ajson.begin(consumer)
        for p in r:
            pass
        assert_that(consumer.registerProducer, called().times(1))
        assert_that(consumer.write, called())
        assert_that(consumer.unregisterProducer, called().times(1))
        assert_that(ajson.begin, called())


class PageTest(unittest.TestCase):

    def setUp(self):
        pass


class RouteTest(unittest.TestCase):

    def test_compile(self):
        route = Route('GET', '/test', lambda ignore: 'Test Done')
        route.compile()
        self.assertEquals(route.match.pattern, '^/test$')
        route.url = '/test/<int:userId>'
        route.compile()
        self.assertEquals(route.match.pattern, '^/test/(?P<userId>\\d+)$')
        route.url = '/test/<float:userId>'
        route.compile()
        self.assertEquals(
            route.match.pattern, '^/test/(?P<userId>\\d+.?\\d*)$'
        )
        route.url = '/test/<userName>'
        route.compile()
        self.assertEquals(route.match.pattern, '^/test/(?P<userName>([^/]+))$')

    def test_validate(self):
        route = Route('GET', '/test/<int:uderId>', lambda ignore: 'Test Done')
        route.compile()

        with Stub() as dispatcher:
            dispatcher.url = '/test/102'

        self.assertEquals(route.validate(dispatcher), route)

        with Stub() as dispatcher:
            dispatcher.url = '/test'

        self.assertEquals(route.validate(dispatcher), None)

    def test__call__(self):

        controller = Collaborator()
        route = controller.callback.route
        route.compile()

        with Stub() as dispatcher:
            dispatcher.url = '/test/102/10.1/test'

        r = route.validate(dispatcher)
        self.assertEquals(r(controller, None), 'User 102 10.1 test')


class RouterTest(unittest.TestCase):

    @defer.inlineCallbacks
    def test_dispatch_route(self):

        controller = StubController()
        request = DummyRequest(['/test/102'])
        request.content = StringIO()
        request.requestHeaders = Headers()

        result = yield controller.render(request)
        self.assertIsInstance(result, response.Ok)
        self.assertEqual(result.subject, 'User ID : 102')
        self.assertEqual(result.headers.get('content-type'), 'text/plain')

    @defer.inlineCallbacks
    def test_dispatch_route_not_found(self):

        controller = StubController()
        request = DummyRequest(['/unknown'])

        result = yield controller.render(request)
        self.assertIsInstance(result, response.NotFound)

    @defer.inlineCallbacks
    def test_dispatch_route_internal_server_error(self):

        controller = StubController()
        request = DummyRequest(['/test/102'])
        request.content = StringIO()
        request.requestHeaders = False

        result = yield controller.render(request)
        self.assertIsInstance(result, response.InternalServerError)

    @defer.inlineCallbacks
    def test_dispatch_route_bad_request(self):

        controller = StubController()
        request = Spy()

        result = yield controller.render(request)
        self.assertIsInstance(result, response.BadRequest)


class Collaborator(object):

    @decoroute('/test/<int:user_id>/<float:arg2>/<text>')
    def callback(self, request, user_id, arg2, text, **kwargs):
        return 'User {} {} {}'.format(user_id, arg2, text)


class StubController(object):

    def __init__(self):
        self.path = ''
        self._router = Router()
        self._router.install_routes(self)

    def render(self, request):
        return self._router.dispatch(self, request)

    def get_register_path(self):
        return self.path

    @decoroute('/test/<int:user_id>')
    def test(self, request, user_id, **kwargs):
        return 'User ID : {}'.format(user_id)
