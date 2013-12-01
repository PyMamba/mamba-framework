# -*- test-case-name: mamba.test.test_services -*-
# Copyright (c) 2013 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: herokuservice
    :platform: Unix, Windows
    :synopsis: Just a Heroku pinger to don't allow it go sleep idle

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

from twisted.python import log
from twisted.web.client import Agent
from twisted.application import service
from twisted.internet import task, reactor
from twisted.web.http_headers import Headers

from mamba.utils import config, heroku


class HerokuService(service.Service):
    """This service maintainss heroku active and don't allow it to go sleep

    .. versionadded:: 0.3.6
    """

    def __init__(self):
        self.name = 'HerokuService'
        self.on_heroku = heroku.are_we_on_heroku()
        self.allowed = config.Application().force_heroku_awake
        self.ping_task = task.LoopingCall(self.ping)

    def startService(self):
        if self.on_heroku and self.allowed and not self.running:
            self.ping_task.start(300)  # run each five minutes
            service.Service.startService(self)

    def stopService(self):
        if self.running:
            self.ping_task.stop()
            service.Service.stopService(self)

    def ping(self):
        """Ping our application to not allow heroku idle it
        """

        if config.Application().heroku_url is None:
            return

        heroku_url = config.Application().heroku_url
        log.msg('Heroku Awakner: Pinging {}'.format(heroku_url))
        return Agent(reactor).request(
            'POST', str(heroku_url),
            Headers({'User-Agent': ['Mamba Heroku Web Client']}),
            None
        )
