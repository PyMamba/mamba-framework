# -*- test-case-name: mamba.test.test_database -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: postgres_adapter
    :platform: Unix, Windows
    :synopsis: PostgreSQL adapter for create SQLite tables

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

from zope.interface import implements
from twisted.python import components

from mamba.core.interfaces import IMambaSQL
from mamba.core.adapters import MambaSQLAdapter


class PostgreSQL:
    """
    This class implements the PostgreSQL syntax layer for mamba

    :param module: the module to generate PostgreSQL syntax for
    :type module: :class:`~mamba.Model`
    """

    implements(IMambaSQL)

    def __init__(self, model):
        self.model = model

    @staticmethod
    def register():
        """Register this component"""

        try:
            components.registerAdapter(MambaSQLAdapter, PostgreSQL, IMambaSQL)
        except ValueError:
            # component already registered
            pass
