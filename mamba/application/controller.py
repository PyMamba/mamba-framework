# -*- test-case-name: mamba.test.test_mamba -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: controller
    :platform: Linux
    :synopsis: Controllers for web projects that encapsulates twisted
               low-level resources using werkzeug routing system.

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

from twisted.web import http
from twisted.python import log
from twisted.web import server
from twisted.web import resource
from twisted.internet import reactor

from mamba import plugin
from mamba.web import routing
from mamba.core import module
from mamba.web import asyncjson
from mamba.utils.output import bold


__all__ = [
    'ControllerError', 'ControllerProvider', 'Controller', 'ControllerManager'
]


class ControllerError(Exception):
    pass


class ControllerProvider:
    """
    Mount point for plugins which refer to Controllers for our applications.

    Controllers implementing this reference should implements the IController
    interface
    """

    __metaclass__ = plugin.ExtensionPoint


class Controller(resource.Resource):
    """
    Mamba Controller Class define a web accesible resource and its actions.

    .. versionadded:: 0.1
    """

    isLeaf = True
    __router = routing.Router()

    def __init__(self):
        """Initialize."""

        resource.Resource.__init__(self)
        self.__router.install_routes(self)

    def getChild(self, name, request):
        """
        This method is not supposed to be called because we are overriden
        the full route dispatching mechanism already built in Twisted.

        Class variable level isLeaf is supposed to be always True but some
        user can override it in his Controller implementation so we make
        sure that the native twisted behavior is never executed.

        If you need Twisted native url dispatching in your site you should
        use :class:`~twisted.web.resource.Resource` class directly in your
        code.

        :param name: ignored
        :type name: string
        :param request: a :class:`~twisted.web.server.request` specifying
                        meta-information about the request that is being made
                        for this child that is ignored at all.
        :type request: :class:`~twisted.web.server.request`
        """

        # someone is using Controller wrong
        msg = (
            '\n\n'
            '===============================================================\n'
            '                             WARNING\n'
            '===============================================================\n'
            'getChild method has been called by Twisted in the {controller}\n'
            'Controller. That means that you are defining the class level \n'
            'variable `isLeaf` as False, this cause Twisted try to dispatch \n'
            'routes with its own built mechanism instead of mamba routing.\n\n'
            'This is not a fatal error but you should revise your Controller\n'
            'because should be probable that your routing dispatching does\n'
            'not work at all (even the Twisted ones)\n'
            '===============================================================\n'
            '                             WARNING\n'
            '===============================================================\n'
            ''.format(controller=self.__class__.__name__)
        )
        log.msg(bold(msg))

        return self

    def render(self, request):
        """
        Render a given resource.
        See :class:`~twisted.web.resource.IResource`'s render method.

        I try to render a router response from the routing mechanism.

        :param request: the HTTP request
        :type request: :class:`~twisted.web.server.Request`
        """

        try:
            return self.route_dispatch(request)
        except Exception, error:
            self.prepare_headers(request, http.INTERNAL_SERVER_ERROR, {})
            return str(error)

    def sendback(self, result, request):
        """
        Send back a result to the browser

        :param request: the HTTP request
        :type request: :class:`~twisted.web.server.Request`
        :param result: the result for send back to the browser
        :type result: dict
        """

        self.prepare_headers(request, result.code, result.headers)

        try:
            if type(result.subject) is not str:
                d = asyncjson.AsyncJSON(result.subject).begin(request)
                d.addCallback(lambda ignored: request.finish())
                return d
            else:
                request.write(result.subject)
                request.finish()
        except Exception, e:
            log.error(e)
            request.setResponseCode(http.INTERNAL_SERVER_ERROR)
            request.write(e)
            request.finish()

        return

    def prepare_headers(self, request, code, headers):
        """
        Prepare the back response headers

        :param request: the HTTP request
        :type request: :class:`~twisted.web.server.Request`
        :param code: the HTTP response code
        :type code: number
        :param headers: the HTTP headers
        :type headers: dict
        """
        request.setResponseCode(code)
        for header, value in headers.iteritems():
            request.setHeader(header, value)

    def route_dispatch(self, request):
        """
        Dispatch a route if any through the routing dispatcher.

        :param request: the HTTP request
        :type request: :class:`~twisted.web.server.Request`
        :returns: :class:`twisted.internet.defer.Deferred` or
                  :class:`mamba.web.response.WebResponse`
        """

        result = self.__router.dispatch(self, request)

        result.addCallback(self.sendback, request)
        return server.NOT_DONE_YET

    def get_register_path(self):
        """
        Return the controller register path for URL Rewritting
        """

        try:
            return self.__route__
        except AttributeError:
            return ''

    def run(self, port=8080):
        """
        This method is used as a helper for testing purposes while you
        are developing your controllers.

        You should never use this in production.
        """
        factory = server.Site(self)
        reactor.listenTCP(port, factory)
        reactor.run()


class ControllerManager(module.ModuleManager):
    """
    Uses a ControllerProvider to load, store and reload Mamba Controllers

    .. versionadded:: 0.1
    """

    def __init__(self):
        """Initialize"""

        self._module_store = 'application/controller'
        super(ControllerManager, self).__init__()

    def get_controllers(self):
        """Return the pool"""

        return self._modules

    def is_valid_file(self, file_path):
        """
        Check if a file is a Mamba controller file

        :param file_path: the file path of the file to check
        :type file_path: str
        """

        return self._valid_file(file_path, 'mamba-controller')
