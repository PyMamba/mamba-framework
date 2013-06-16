# -*- test-case-name: mamba.core.test.test_packages -*-
# Copyright (c) 2013 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: packages
    :platform: Unix, Windows
    :synopsys: Loadable python modules shared packed resources

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

import os

from twisted.python import log

from mamba.utils.config import InstalledPackages
from mamba.application.model import ModelManager
from mamba.application.controller import ControllerManager


class PackagesManager(object):
    """Load packed shared resources configured to be used on the application
    """

    def __init__(self):
        super(PackagesManager, self).__init__()
        self.packages = {}
        # initialize the configuration and the object
        self.config = InstalledPackages('config/installed_packages.json')
        self.register_packages()

    def register_packages(self):
        """Register packages found in the config file.

        Styles and Scripts are a bit special and we register the main
        application ones here so we can just refer all of them from the
        :class:`mamba.core.resource.Resource` subclasses and they will be
        auto imported in our templates
        """

        log.msg('Registering packages...')
        for package, data in self.config.packages.iteritems():
            log.msg('registring package {}'.format(package))
            try:
                module = __import__(package, globals(), locals())
            except ImportError:
                log.err('{} is not installed on the system'.format(package))
                continue

            path = os.path.dirname(os.path.normpath(module.__file__))
            self.packages[package] = {'path': path}

            if data.get('autoimport', False) is True:
                self.packages[package].update({
                    'controller': ControllerManager(
                        '{}/controller'.format(path), package
                    ),
                    'model': ModelManager(
                        '{}/model'.format(path), package
                    )
                })
