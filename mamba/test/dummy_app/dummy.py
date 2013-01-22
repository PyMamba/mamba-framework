# This file is part of Mamba Dummy Application
# Copyright (c) 2012 - 2013 Oscar Campos <oscar.campos@member.fsf.org>

"""
.. module:: dummy
    :platform: Linux
    :synopsis: Dummy application for testing purposes

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>
"""

from twisted.web import server
from twisted.python import log
from twisted.application import service

from mamba import Mamba
from mamba.web import Page


def MambaApplicationFactory(settings):
    # load the configuration
    application = service.Application(settings.name)

    # register settings through Mamba Borg
    app = Mamba(settings)
    # we need log at routing registration so open log file
    log.startLogging(open('twistd.log', 'w+'))

    # create the root page
    root = Page(app)

    # create the site
    mamba_app_site = server.Site(root)

    return mamba_app_site, application
