# -*- test-case-name: mamba.test.test_controller -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: controller
    :platform: Linux
    :synopsis: Controllers for web projects that encapsulates twisted
               low-level resources using custom routing system.

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

from os.path import normpath

from twisted.python import log
from twisted.internet import reactor
from twisted.web import http, server

from mamba import plugin
from mamba.web import routing
from mamba.web import asyncjson
from mamba.utils.output import bold
from mamba.core import module, resource


__all__ = [
    'ControllerError', 'ControllerProvider', 'Controller', 'ControllerManager'
]


class ControllerError(Exception):
    """Raised on controller errors
    """

    pass


class ControllerProvider:
    """
    Mount point for plugins which refer to Controllers for our applications.

    Controllers implementing this reference should implements the IController
    interface
    """

    __metaclass__ = plugin.ExtensionPoint


class Controller(resource.Resource, ControllerProvider):
    """
    Mamba Controller Class define a web accesible resource and its actions.

    A controller can (and should) be attached to a
    :class:`twisted.web.resource.Resource` as a child or to others
    :class:`~mamba.Controller`.

    Unlike :class:`twisted.web.resource.Resource`, :class:`~mamba.Controller`
    don't use the Twisted URL dispatching mechanism. The
    :class:`~mamba.Controller` uses :class:`~mamba.web.Router` for URL
    dispatching through the :py:func:`~mamba.application.route` decorator::

        @route('/hello_world', method='GET')
        def helloworld(self, request, **kwargs):
            return 'Hello World'

    seealso: :class:`~mamba.web.Router`, :class:`~mamba.web.Route`

    """

    isLeaf = True
    _router = routing.Router()

    def __init__(self):
        """Initialize
        """

        resource.Resource.__init__(self)
        self._router.install_routes(self)

    def getChild(self, name, request):
        """
        This method is not supposed to be called because we are overriden
        the full route dispatching mechanism already built in Twisted.

        Class variable level :attr:`isLeaf` is supposed to be always
        :keyword:`True` but any users can override it in their
        :class:`~mamba.Controller` implementation so we make sure that the
        native twisted behavior is never executed.

        If you need Twisted native url dispatching in your site you should
        use :class:`~twisted.web.resource.Resource` class directly in your
        code.

        :param name: ignored
        :type name: string
        :param request: a :class:`twisted.web.server.Request` specifying
                        meta-information about the request that is being made
                        for this child that is ignored at all.
        :type request: :class:`~twisted.web.server.Request`
        :rtype: :class:`~mamba.Controller`
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
        see: :class:`twisted.web.resource.IResource`'s render method.

        I try to render a router response from the routing mechanism.

        :param request: the HTTP request
        :type request: :class:`twisted.web.server.Request`
        """

        try:
            return self.route_dispatch(request)
        except Exception as error:
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
        except Exception as error:
            log.err(error)
            request.setResponseCode(http.INTERNAL_SERVER_ERROR)
            request.write(error)
            request.finish()

        return

    def prepare_headers(self, request, code, headers):
        """
        Prepare the back response headers

        :param request: the HTTP request
        :type request: :class:`~twisted.web.server.Request`
        :param code: the HTTP response code
        :type code: int
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

        result = self._router.dispatch(self, request)

        result.addCallback(self.sendback, request)
        return server.NOT_DONE_YET

    def get_register_path(self):
        """Return the controller register path for URL Rewritting
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
    Uses a ControllerProvider to load, store and reload Mamba Controllers.

    :attr:`_model_store` A private attribute that sets the prefix
    path for the controllers store
    :param store: if is not None it sets the _module_store attr
    """

    def __init__(self, store=None):
        """Initialize
        """

        self._module_store = 'application/controller' if not store else store
        super(ControllerManager, self).__init__()

    def get_controllers(self):
        """Return the controllers pool
        """

        return self._modules

    def is_valid_file(self, file_path):
        """
        Check if a file is a Mamba controller file

        :param file_path: the file path of the file to check
        :type file_path: str
        """

        if type(file_path) is not str:
            return self._valid_file(
                normpath('{}/{}'.format(
                    self._module_store, file_path.basename())
                ),
                'mamba-controller'
            )

        return self._valid_file(
            normpath('{}/{}'.format(self._module_store, file_path)),
            'mamba-controller'
        )
