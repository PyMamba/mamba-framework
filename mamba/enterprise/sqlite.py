# -*- test-case-name: mamba.test.test_database -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: sqlite_adapter
    :platform: Unix, Windows
    :synopsis: SQLite adapter for create SQLite tables

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

from storm import variables
from twisted.python import components

from mamba.core.interfaces import IMambaSQL
from mamba.core.adapters import MambaSQLAdapter


class SQLite:
    """
    This class implements the SQLite syntax layer for mamba

    :param module: the module to generate SQLite syntax for
    :type module: :class:`~mamba.Model`
    """

    def __init__(self, model):
        self.module = model

    def parse_column(self, column):
        """
        Parse a Storm column to the correct SQLite value type. For example,
        if we pass a column of type :class:`storm.variable.IntVariable` with
        name `amount` we get back:

            amount INTEGER

        :param column: the Storm properties column to parse
        :type column: :class:`storm.properties`
        """

        if (column.variable_class is variables.UnicodeVariable
                or column.variable_class is variables.DecimalVariable
                or column.variable_class is variables.DateVariable
                or column.variable_class is variables.DateTimeVariable
                or column.variable_class is variables.TimeVariable
                or column.variable_class is variables.TimeDeltaVariable
                or column.variable_class is variables.ListVariable):
            column_type = 'VARCHAR'
        elif (column.variable_class is variables.IntVariable
                or column.variable_class is variables.BoolVariable):
            column_type = 'INTEGER'
        elif column.variable_class is variables.FloatVariable:
            column_type = 'REAL'
        elif (column.variable_class is variables.RawStrVariable
                or column.variable_class is variables.PickleVariable
                or column.variable_class is variables.JSONVariable):
            column_type = 'BLOB'
        else:
            column_type = 'TEXT'  # fallback to TEXT (tears are comming)

        column_type = '{} {}'.format(
            column._detect_attr_name(self.model.__class__),
            column_type
        )
        return column_type

    @staticmethod
    def register():
        """Register this component"""

        components.registerAdapter(MambaSQLAdapter, SQLite, IMambaSQL)
