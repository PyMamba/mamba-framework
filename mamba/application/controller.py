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

import json

from zope.interface import implements
from twisted.web import resource

from mamba import plugin
from mamba.web import asyncjson
from mamba.core import module
from mamba.core import interfaces


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
    implements(interfaces.IController)

    def __init__(self):
        """Initialize."""
        resource.Resource.__init__(self)

    def getChild(self, name, request):
        """
        This method retrieves a static or dynamic 'child' resource from it.

        First checks if a resource was manually added using putChild, and
        then call getChild to check for dynamic resources.

        :param name: a strign, describing the child
        :type name: str
        :param request: a :class:`~twisted.web.server.request` specifying
                        meta-information about the request that is being made
                        for this child.
        :type request: :class:`~twisted.web.server.request`
        """

        if hasattr(self, name):
            return self
        return resource.Resource.getChild(self, name, request)

    def render(self, request):
        """
        Render a given resource.
        See :class:`~twisted.web.resource.IResource`'s render method.

        I try to render an action from myself, if action does not exists just
        return the :class:`~twisted.resource.Resource.render` result
        from Twisted.

        If action_name exists but no action is defined I'll return result for
        :class:`~twisted.resource.Resource.render`.

        :param request: the HTTP request
        :type request: :class:`~twisted.web.server.Request`
        """

        kwargs = {}
        for k, v in request.args.iteritems():
            kwargs[k] = v
        if len(request.prepath) > 1:
            return getattr(self, request.prepath[1])(request, **kwargs)
        action_name = kwargs.get('action', None)
        if not action_name:
            return resource.Resource.render(self, request)
        action = getattr(self, action_name[0], None)
        if not action:
            return resource.Resource.render(self, request)
        return action(request, **kwargs)

    def senderrback(self, request, error):
        """
        Send back errors to the browser

        :param request: the HTTP request
        :type request: :class:`~twisted.web.server.Request`
        :param error: the error dict containing `message` and `number`
        :type error: dict
        """
        request.write(json.dumps({
            'success': False,
            'message': error['message'],
            'error': error['number']
        }))
        request.finish()

    def sendback(self, request, result):
        """
        Send back a result to the browser

        :param request: the HTTP request
        :type request: :class:`~twisted.web.server.Request`
        :param result: the result for send back to the browser
        :type result: dict
        """
        d = asyncjson.AsyncJSON(result).begin(request)
        d.addCallback(lambda ignored: request.finish())


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

        return self.__is_valid(file_path, 'mamba-controller')
