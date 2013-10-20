# -*- test-case-name: mamba.test.test_web -*-
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

import os

from mamba.web import stylesheet
from mamba.utils.config import InstalledPackages


class AppStyles(object):
    """
    Manager for Application Stylesheets

    seealso: :class:`~mamba.web.Stylesheet`
    """

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
            self.managers.append(stylesheet.StylesheetManager(
                '{}/view/stylesheets'.format(path))
            )

        # local application
        self.managers.append(
            stylesheet.StylesheetManager('application/view/stylesheets')
        )

        self.setup()

    def setup(self):
        """Setup the managers
        """

        for manager in self.managers:
            manager.setup()

    def get_styles(self):
        """
        Return the :class:`mamba.Stylesheet` pool
        """

        styles = {}
        for manager in self.managers:
            styles.update(manager.stylesheets)

        return styles


__all__ = ['AppStyles']
