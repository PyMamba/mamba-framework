# -*- test-case-name: mamba.test.test_web -*-
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

from mamba.web import stylesheet


__all__ = ['AppStyles']


class AppStyles(stylesheet.StylesheetManager):
    """
    Manager for Application Stylesheets

    seealso: :class:`~mamba.web.Stylesheet`
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
        Return the :class:`mamba.Stylesheet` pool
        """

        return self.stylesheets
