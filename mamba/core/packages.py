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
    """
    The PackagesManager is used to register the shared packages that our
    mamba applications are going to import and use. The manager is instanced
    once by the :class:`~mamba.application.app.Mamba` borg and create and
    load controllers and models managers for every package that we want to
    use in our application.

    :param config_file: the path to config file that we want to use
    :type config_file: str

    .. versionadded:: 0.3.6
    """

    def __init__(self, config_file='config/installed_packages.json'):
        super(PackagesManager, self).__init__()
        self.packages = {}
        # initialize the configuration and the object
        self.config = InstalledPackages(config_file)
        self.register_packages()

    def register_packages(self):
        """Register packages found in the config file.

        Styles and Scripts are a bit special and we register the main
        application ones here so we can  refer all of them from the
        :class:`~mamba.core.resource.Resource` subclasses and they will be
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
            self.packages[package].update({
                'model': ModelManager('{}/model'.format(path), package)
            })

            if data.get('autoimport', False):
                self.packages[package].update({
                    'controller': ControllerManager(
                        '{}/controller'.format(path), package
                    )
                })
