# -*- test-case-name: mamba.test.test_web -*-
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

from mamba.web import stylesheet


__all__ = ['AppStyles']


class AppStyles(stylesheet.StylesheetManager):
    """
    Manager for Application Stylesheets

    .. versionadded:: 0.1
    """

    def __init__(self):
        """
        Initialize
        """

        self._styles_store = 'application/view/stylesheets'
        super(AppStyles, self).__init__()

        self.setup()

    def get_styles(self):
        """
        Return the pool
        """

        return self.stylesheets
