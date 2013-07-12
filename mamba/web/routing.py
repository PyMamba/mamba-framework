# -*- test-case-name: mamba.test.test_web -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module: routing
    :platform: Unix, Windows
    :synopsis: Mamba routing system

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>
"""

import re
import json
import inspect
import logging
import functools
from singledispatch import singledispatch
from collections import defaultdict, OrderedDict

from twisted.python import log
from twisted.internet import defer
from twisted.web.http import parse_qs

from mamba.web import response
from mamba.utils import output, config
from mamba.utils.converter import Converter
from mamba.web.url_sanitizer import UrlSanitizer


class UrlRegex(object):
    """Common static URL regex
    """

    url_matcher = re.compile(r'<(int|float|):?([^/]+)>')
    type_regex = {
        'int': r'(?P<type>\d+)',
        'float': r'(?P<type>\d+.?\d*)',
        '': r'(?P<type>([^/]+))'
    }
    html_regex = re.compile(
        r"(?i)<\/?\w+((\s+\w+(\s*=\s*(?:\\?\".*?"
        "\"|\\?'.*?'|[^'\">\s]+))?)+\s*|\s*)\/?>"
    )


class Route(object):
    """I am a Route in the Mamba routing system.
    """

    def __init__(self, method, url, callback):
        """
        Initializes the Route object with the given data from decorator

        :param method: the HTTP method
        :type method: string
        :param url: the URL path
        :type url: string
        :param callback: the callable callback
        :type callback: callabe object
        """
        self.url = url
        self.match = ''
        self.arguments = OrderedDict()
        self.method = method
        self.callback = callback
        self.callback_args = {}

        super(Route, self).__init__()

    def compile(self):
        """
        Compiles the regex matches using the complete URL
        """

        url_matcher = '^{url}$'.format(url=self.url)

        for match in UrlRegex.url_matcher.findall(self.url):
            if not match[0]:  # string
                url_matcher = url_matcher.replace(
                    '<{}>'.format(match[1]),
                    UrlRegex.type_regex[match[0]].replace('type', match[1])
                )
            else:
                url_matcher = url_matcher.replace(
                    '<{}:{}>'.format(*match),
                    UrlRegex.type_regex[match[0]].replace('type', match[1])
                )

            self.arguments.update({
                match[1]: None if not match[0] else eval(match[0])
            })

        self.match = re.compile(url_matcher)

    def validate(self, dispatcher):
        """
        Validate a given path against stored URLs. Returns None if
        nothing matched itself otherwise

        :param dispatcher: the dispatcher object that containing the
                           information to validate
        :type dispatcher: :class:`~mamba.web.RouteDispatcher`
        """

        group = self.match.search(dispatcher.url)
        if group is not None:
            self.callback_args = group.groupdict()

            if len(self.callback_args):
                for key, value in self.callback_args.iteritems():
                    if self.arguments.get(key) is not None:
                        # convert to the correct type
                        self.callback_args.update({
                            key: self.arguments.get(key)(value)
                        })

            return self

        return None

    def __repr__(self):
        return 'Route({})'.format(', '.join(
            map(repr, [self.method, self.url, self.callback, self.arguments]))
        )

    def __call__(self, controller, request):
        """
        Make sure we call the decorated method with the correct args

        :param request: the HTTP request
        :type request: :class:`~twisted.web.server.Request`
        """

        return self.callback(controller, request, **self.callback_args)


class Router(object):
    """
    I store, lookup, cache and dispatch routes for Mamba

    A route is stores as:
        [methods][route][Controller.__class__.__name__]
    """

    def __init__(self):

        self.routes = {
            'GET': defaultdict(dict),
            'POST': defaultdict(dict),
            'PUT': defaultdict(dict),
            'DELETE': defaultdict(dict),
            'OPTIONS': defaultdict(dict),
            'PATCH': defaultdict(dict),
            'HEAD': defaultdict(dict)
        }

        self._prepare_response = singledispatch(self._prepare_response)
        self._prepare_response.register(str, self._prepare_response_str)
        self._prepare_response.register(
            response.Response, self._prepare_response_object)

        super(Router, self).__init__()

    def dispatch(self, controller, request):
        """Dispatch a route and return back the appropiate response.

        :param controller: the mamba controller
        :type controller: :class:`~mamba.Controller`
        :param request: the HTTP request
        :type request: :class:`twisted.web.server.Request`
        """

        try:
            route = RouteDispatcher(self, controller, request).lookup()

            if type(route) is Route:
                # at this point we can get a Deferred or an inmediate result
                # depending on the user code
                result = defer.maybeDeferred(route, controller, request)
                result.addCallback(self._process, request)
                result.addErrback(self._process_error, request)
            elif route == 'NotImplemented':
                result = defer.succeed(response.NotImplemented(
                    UrlSanitizer().sanitize_container(
                        [controller.get_register_path()] + request.postpath
                    )
                ))
            else:
                msg = 'ERROR 404: {} not found'.format(
                    UrlSanitizer().sanitize_container(
                        [controller.get_register_path()] + request.postpath
                    )
                )
                result = defer.succeed(response.NotFound(
                    msg,
                    {'content-type': 'text/plain'}
                ))
        except TypeError as error:
            log.msg(error, logLevel=logging.WARN)
            result = defer.succeed(response.BadRequest(
                str(error),
                {'content-type': 'text/plain'}
            ))
        except Exception as error:
            log.err(error)
            result = response.InternalServerError(
                'ERROR 500: Internal server error: {}\n\t{}'.format(
                    type(error), error
                )
            )

        return result

    def install_routes(self, controller):
        """Install all the routes in a controller.

        :param controller: the controller where to fid routes
        :type controller: :class:`~mamba.Controller`
        """

        for func in inspect.getmembers(controller, predicate=inspect.ismethod):
            error = False
            if hasattr(func[1], 'route'):
                route = getattr(func[1], 'route')
                route.url = UrlSanitizer().sanitize_string(
                    controller.get_register_path() + route.url
                )
                route.compile()
                # normalize parameters
                real_args = inspect.getargspec(route.callback)[0]
                if real_args:
                    real_args = real_args[real_args.index('request') + 1:]
                    for arg in real_args:
                        if arg not in route.arguments.keys():
                            green = output.darkgreen
                            log.msg(
                                '{ERROR}: {arg} is not present in the {rout} '
                                'url for function {func_name}. Please, revise '
                                'your @route url string. The paramters names '
                                'in the url string should match the ones in '
                                'the function call. Skipping route registering'
                                '... this route ({route}) shouldn\'t be'
                                ' available at {controller}'.format(
                                    ERROR=output.brown('ERROR'),
                                    rout=green('@route'),
                                    arg=output.darkgreen(arg),
                                    func_name=green(route.callback.__name__),
                                    route=green('@route -> {}'.format(
                                        route.url
                                    )),
                                    controller=green(
                                        controller.__class__.__name__
                                    )
                                )
                            )
                            error = True

                if not error:
                    self.register_route(controller, route)

    def register_route(self, controller, route):
        """Decorator that register a route for the given controller

        :param controller: the controller where to register the route
        :type controller: :class:`~mamba.Controller`
        :param route: the :class:`~mamba.Route` to register
        :type route: :class:`~mamba.web.Route`
        """

        controller_name = controller.__class__.__name__

        if getattr(config.Application(), 'debug', False):
            bold = output.bold
            log.msg(
                bold('Registering route:') + ' {route}'.format(route=route))

        self.routes[route.method][route.url][controller_name] = route

    # decorator
    def route(self, url, method='GET'):
        """Register routes for controllers or full REST resources.
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func

            setattr(wrapper, 'route', Route(method, url, func))

            return wrapper

        return decorator

    def _process(self, result, request):
        """Prepare and process the result.
        """

        if result is None:
            return response.Response(209, None)

        try:
            return self._prepare_response(result, request)
        except Exception as error:
            return self._process_error(result, request, error)

    def _process_error(self, result, request, error=''):
        """Process and sendback an error response
        """

        if isinstance(error, response.Response):
            error = error.subject

        log.err('Deferred failed: {error}'.format(error=error))

        return response.InternalServerError(
            'ERROR 500: Internal server error {}\n{}'.format(error, result)
        )

    def _prepare_response(self, result, request):
        """Renders the result to cobvert it to the appropiate format
        """

        result = Converter.serialize(result)
        headers = {'content-type': 'application/json'}
        retval = response.Ok(result, headers)

        return retval

    def _prepare_response_str(self, result, request):
        """Renders the result into 'text/html' or 'text/plain' content-type
        """

        if re.match(UrlRegex.html_regex, result):
            result = response.Ok(result, {'content-type': 'text/html'})
        else:
            result = response.Ok(result, {'content-type': 'text/plain'})

        return result

    def _prepare_response_object(self, result, request):
        """Renders the result.subject into JSON if needed
        """

        if 'application/json' in result.headers.values():
            result.subject = Converter.serialize(result.subject)

        return result


class RouteDispatcher(object):
    """Look for a route, compile/process if neccesary and return it
    """

    def __init__(self, router, controller, request):
        self.router = router
        self.request = request
        self.method = request.method
        self.controller = controller.__class__.__name__
        self.url = UrlSanitizer().sanitize_container(
            [controller.get_register_path()] + request.postpath
        )

    def lookup(self):
        """
        I traverse the URLs at router picking up the ones that match the
        controller name and then process it to validate which ones match
        by path/arguments to a particular Route

        If nothing match just returns None
        """

        # postpath '/' is not allowed when using mamba routing
        if len(self.request.postpath) and self.request.postpath[0] == '':
            return None

        for controllers in self.router.routes[self.method].values():
            if self.controller in controllers:
                route = controllers.get(self.controller).validate(self)

                if route:
                    self._parse_request_args(route)
                    return route

        for url in self.router.routes.values():
            controllers = url.values()
            if len(controllers):
                for i in xrange(len(controllers)):
                    if self.controller in controllers[i]:
                        r = controllers[i].get(self.controller).validate(self)
                        if r:
                            return 'NotImplemented'

        return None

    def _parse_request_args(self, route):
        """Parses JSON data and request form if present
        """

        data = self.request.content.read()
        data_json = {}

        if self.request.method in ['POST', 'PUT']:
            ct = self.request.requestHeaders.getRawHeaders('content-type')
            if 'application/json' in ct:
                try:
                    data_json = json.loads(data)
                except ValueError:
                    data_json = {}

        request_args = self.request.args
        request_headers = self.request.requestHeaders.getRawHeaders(
            'content-type'
        )

        if self.request.method == 'PUT':
            if 'application/x-www-form-urlencoded' in request_headers:
                request_args = parse_qs(data, 1)

        if len(request_args) > 0:
            for key, value in request_args.iteritems():
                if key not in route.callback_args:
                    route.callback_args.update({key: value[0]})
        elif data_json:
            for key, value in data_json.iteritems():
                if key not in route.callback_args:
                    route.callback_args.update({key: value})

    def __repr__(self):
        return 'RouteDispatcher({})'.format(', '.join(
            map(repr, [self.router, self.request, self.controller, self.url]))
        )
