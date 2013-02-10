# -*- test-case-name: mamba.test.test_web -*-
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

from mamba.web import script


class Scripts(script.ScriptManager):
    """
    Manager for Application Scripts

    seealso: :class:`~mamba.web.Script`
    """

    def __init__(self):
        """
        Initialize
        """

        self._scripts_store = 'application/view/scripts'
        super(Scripts, self).__init__()

        self.setup()

    def get_scripts(self):
        """
        Return the :class:`mamba.Scripts` pool
        """

        return self.scripts


__all__ = ['Scripts']
