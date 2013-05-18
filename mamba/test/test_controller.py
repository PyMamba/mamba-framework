
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
Tests for mamba.application.controller
"""

import sys
import urllib
from cStringIO import StringIO
from collections import OrderedDict

from twisted.internet import defer
from twisted.trial import unittest
from twisted.python import filepath
from twisted.web import resource, server
from twisted.web.http_headers import Headers
from twisted.web.test.test_web import DummyRequest
from doublex import Spy, ProxySpy, assert_that, ANY_ARG, called

from mamba.core import GNU_LINUX
from mamba.web.routing import Router
from mamba.test.dummy_app.application.controller.dummy import DummyController

from mamba.web.response import Ok
from mamba.application import controller
from mamba.core.interfaces import INotifier


class ControllerRequest(DummyRequest):
    """
    Dummy Request object needed to routing system
    """

    def __init__(self, postpath, params, session=None):
        self.content = StringIO()
        self.content.write(urllib.urlencode(params))
        self.content.seek(0, 0)
        self.requestHeaders = Headers()

        DummyRequest.__init__(self, postpath, session)


class ControllerTest(unittest.TestCase):
    """
    Tests for mamba.application.controller. I'm not goig to test the already
    well tested twisted.web.resource object here so those are really short
    and dumb tests.
    """

    def setUp(self):
        self.resource = Spy(resource.Resource)
        self.c = controller.Controller()

    def get_request(self):

        with Spy() as request:
            request.registerProducer(ANY_ARG)
            request.unregisterProducer()
            request.write(ANY_ARG)
            request.setResponseCode(ANY_ARG)
            request.setHeader(ANY_ARG)

        return request

    def test_class_inherits_twisted_web_resource(self):
        self.assertTrue(issubclass(controller.Controller, resource.Resource))

    def test_is_leaf(self):
        self.assertTrue(self.c.isLeaf)

    def test_getchild_returns_itself_always(self):
        request = self.get_request()
        self.assertIdentical(self.c.getChild('test', request), self.c)
        self.c.isLeaf = False
        self.assertIdentical(self.c.getChild('test', request), self.c)

    @defer.inlineCallbacks
    def test_send_back(self):

        request = DummyRequest(['/test'], '')
        result = Ok('Testing', {'content-type': 'application/json'})

        request = request
        result = yield self.c.sendback(result, request)

        self.assertEqual(result, None)
        self.assertEqual(request.written[0], 'Testing')

    def test_register_path_returns_empty(self):
        self.assertEqual(self.c.get_register_path(), '')

    @defer.inlineCallbacks
    def test_controller_render_delegates_on_routing(self):

        c = DummyController()

        router = ProxySpy(Router())
        c._router = router
        # request = self.get_request()
        request = ControllerRequest(['/test'], {})
        r = yield self._render(c, request)

        assert_that(router.dispatch, called().times(1))
        self.assertEqual(r.written[0], 'ERROR 404: /dummy/test not found')

    def test_prepare_headers_works(self):

        request = self.get_request()
        self.c.prepare_headers(request, 200, {'content-type': 'x-test'})

        assert_that(request.setResponseCode, called().with_args(200).times(1))
        assert_that(
            request.setHeader,
            called().with_args('content-type', 'x-test').times(1)
        )

    def _render(self, controller, request):
        result = controller.render(request)
        if result is server.NOT_DONE_YET:
            if request.finished:
                return defer.succeed(request)
            else:
                return request.notifyFinish().addCallback(lambda _: request)
        else:
            raise ValueError('Unexpected return value: {}'.format(result))


class ControllerManagerTest(unittest.TestCase):
    """
    Tests for mamba.application.controller.ControllerManager
    """

    def setUp(self):
        self.mgr = controller.ControllerManager()

        if GNU_LINUX:
            self.addCleanup(self.mgr.notifier.loseConnection)

    def load_manager(self):
        sys.path.append('../mamba/test/dummy_app')
        self.mgr.load(
            '../mamba/test/dummy_app/application/controller/dummy.py')

    def test_inotifier_provided_by_controller_manager(self):
        if not GNU_LINUX:
            raise unittest.SkipTest('File monitoring only available on Linux')
        self.assertTrue(INotifier.providedBy(self.mgr))

    def test_get_controllers_is_ordered_dict(self):
        self.assertIsInstance(self.mgr.get_controllers(), OrderedDict)

    def test_get_controllers_is_empty(self):
        self.assertNot(self.mgr.get_controllers())

    def test_is_valid_file_works_on_valid(self):
        import os
        currdir = os.getcwd()
        os.chdir('../mamba/test/dummy_app/')
        self.assertTrue(self.mgr.is_valid_file('dummy.py'))
        os.chdir(currdir)

    def test_is_valid_file_works_on_invalid(self):
        self.assertFalse(self.mgr.is_valid_file('./test.log'))

    def test_is_valid_file_works_with_filepath(self):
        import os
        currdir = os.getcwd()
        os.chdir('../mamba/test/dummy_app/')
        self.assertTrue(self.mgr.is_valid_file(filepath.FilePath('dummy.py')))
        os.chdir(currdir)

    def test_is_loading_modules_works(self):
        self.load_manager()
        self.assertTrue(self.mgr.length() != 0)

    def test_lookup(self):
        unknown = self.mgr.lookup('unknown')
        self.assertEqual(unknown, {})

        self.load_manager()
        dummy = self.mgr.lookup('dummy').get('object')
        self.assertTrue(dummy.name == 'Dummy')
        self.assertTrue('I am a dummy controller' in dummy.desc)
        self.assertTrue(dummy.loaded)

    def test_reload(self):
        self.load_manager()

        dummy = self.mgr.lookup('dummy').get('object')

        self.mgr.reload('dummy')
        dummy2 = self.mgr.lookup('dummy').get('object')

        self.assertNotEqual(dummy, dummy2)
