# This file is part of ${application}
# Copyright (c) ${year} - ${author} <${author_email}>

"""
.. module:: ${application}
    :platform: ${platforms}
    :synopsis: ${synopsis}

.. moduleauthor:: ${author} <${author_email}>
"""

from twisted.web import server
from twisted.application import service

from mamba import Mamba
from mamba.web import Page


def MambaApplicationFactory(settings):
    # load the configuration
    application = service.Application(settings.name)

    # register settings through Mamba Borg
    app = Mamba(settings)

    # create the root page
    root = Page(app)

    # create the site
    mamba_app_site = server.Site(root)

    return mamba_app_site, application
