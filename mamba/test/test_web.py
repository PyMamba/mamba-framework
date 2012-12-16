
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
Tests for mamba.web
"""

from twisted.trial import unittest
from twisted.web.server import Request
from doublex import ProxySpy, Stub, Spy, ANY_ARG, called, assert_that, is_

from mamba.web import stylesheet, page, asyncjson


class StylesheetTest(unittest.TestCase):

    def setUp(self):
        pass


class AsyncJSONTest(unittest.TestCase):

    def test_asyncjson_works_as_expected(self):

        consumer = Spy(Request)

        ajson = ProxySpy(asyncjson.AsyncJSON({'id': 1, 'name': 'Test'}))
        d = ajson.begin(consumer)
        d.addCallback(
            lambda: assert_that(consumer.registerProducer, called().times(1))
        )
        d.addCallback(lambda: assert_that(consumer.write, called().times(1)))
        d.addCallback(
            lambda: assert_that(consumer.unregisterProducer, called().times(1))
        )
        d.addCallback(lambda: assert_that(ajson._produce, called()))
        d.addCallback(lambda: assert_that(ajson._unregister, called()))
        d.addCallback(lambda: assert_that(ajson.stop, called()))


class PageTest(unittest.TestCase):

    def setUp(self):
        pass


class RoutingTest(unittest.TestCase):

    pass
