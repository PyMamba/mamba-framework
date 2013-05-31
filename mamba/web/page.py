# -*- test-case-name: mamba.test.test_web -*-
# Copyright (c) 2012 - 2013 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module: page
    :platform: Unix, Windows
    :synopsis: The Page object is the main web application entry point

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>
"""

from twisted.python import log
from twisted.internet import reactor
from twisted.web import static, server
from twisted.python.logfile import DailyLogFile

from mamba.core import resource


class Page(resource.Resource):
    """
    This represents a full web page in mamba applications. It's usually
    the root page of your web site/application.

    :param app: The Mamba Application that implements this page
    :type app: :class:`~mamba.application.app.Application`
    """

    def __init__(self, app):
        resource.Resource.__init__(self)

        self.app = app
        self._controllers_manager = None
        self._stylesheets = []
        self._scripts = []

        # register log file if any
        if (app.development is False and
                app.already_logging is False and app.log_file is not None):
            log.startLogging(DailyLogFile.fromFullPath(app.log_file))

        # set managers
        self._controllers_manager = app.managers.get('controller')

        # register controllers
        self.register_controllers()

    def add_script(self, script):
        """Adds a script to the page
        """

        self.putChild(script.prefix, static.File(script.path))

    def register_controllers(self):
        """Add a child for each controller in the ControllerManager
        """

        for controller in self._controllers_manager.get_controllers().values():
            log.msg(
                'Registering controller {} with route {} {}({})'.format(
                    controller.get('object').name,
                    controller.get('object').get_register_path(),
                    controller.get('object').name,
                    controller.get('module')
                )
            )

            self.putChild(
                controller.get('object').get_register_path(),
                controller.get('object')
            )

    def run(self, port=8080):
        """
        Method to run the application within Twisted reactor

        This method exists for testing purposes only and fast
        controller test-development-test workflow. In production you
        should use twistd

        :param port: the port to listen
        :type port: number
        """
        factory = server.Site(self)
        reactor.listenTCP(port, factory)
        reactor.run()


__all__ = ['Page']
