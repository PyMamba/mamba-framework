# -*- test-case-name: mamba.test.test_web -*-
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

import os

from mamba.web import script
from mamba.utils.config import InstalledPackages


class AppScripts(object):
    """
    Manager for Application Scripts

    seealso: :class:`~mamba.web.Script`
    """

    # def __init__(self, store=None, package=None):
    def __init__(self, config_file_name='config/installed_packages.json'):
        """
        Initialize
        """

        self.managers = []

        # shared packages
        config = InstalledPackages(config_file_name)
        for package, data in config.packages.iteritems():
            if data.get('use_scripts', False) is False:
                continue

            module = __import__(package, globals(), locals())
            path = os.path.dirname(os.path.normpath(module.__file__))
            self.managers.append(script.ScriptManager(
                '{}/view/scripts'.format(path))
            )

        # local application
        self.managers.append(
            script.ScriptManager('application/view/scripts')
        )

        self.setup()

    def setup(self):
        """Setup the managers
        """

        for manager in self.managers:
            manager.setup()

    def get_scripts(self):
        """
        Return the :class:`mamba.Scripts` pool
        """

        scripts = {}
        for manager in self.managers:
            scripts.update(manager.scripts)

        return scripts


__all__ = ['AppScripts']
