# -*- test-case-name: mamba.test.test_model -*-
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

from mamba.utils import config
from mamba.core.interfaces import IMambaSQL
from mamba.enterprise.common import CommonSQL
from mamba.core.adapters import MambaSQLAdapter


class SQLiteError(Exception):
    """Base class for SQLite related errors
    """


class SQLiteMissingPrimaryKey(SQLiteError):
    """Fired when the model is missing the primary key
    """


class SQLite(CommonSQL):
    """
    This class implements the SQLite syntax layer for mamba

    :param module: the module to generate SQLite syntax for
    :type module: :class:`~mamba.Model`
    """

    def __init__(self, model):
        self.model = model

    def parse_references(self):
        """Just skips because SQLite doen't know anything about foreign keys
        """
        pass

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

        column_type = '{} {}{}{}'.format(
            column._detect_attr_name(self.model.__class__),
            column_type,
            self._null_allowed(column),
            self._default(column)
        )
        return column_type

    def detect_primary_key(self):
        """
        Detect the primary key for the model and return it back with the
        correct SQLite syntax

        :returns: a string with the correct SQLite syntax
        :rtype: str
        :raises: SQLiteMissingPrimaryKey on missing primary key
        """

        if not hasattr(self.model, '__storm_primary__'):
            for column in self.model._storm_columns.values():
                if column.primary == 1:
                    return 'PRIMARY KEY({})'.format(column.name)

            raise SQLiteMissingPrimaryKey(
                'SQLite based model {} is missing a primary key column'.format(
                    repr(self.model)
                )
            )

        return 'PRIMARY KEY {}'.format(
            str(self.model.__storm_primary__)
        )

    def create_table(self):
        """Return the SQLite syntax for create a table with this model
        """

        query = 'CREATE TABLE {} (\n'.format((
            'IF NOT EXISTS {}'.format(self.model.__storm_table__) if (
            config.Database().create_table_behaviours.get(
                'create_if_not_exists'))
            else self.model.__storm_table__
        ))

        for i in range(len(self.model._storm_columns.keys())):
            column = self.model._storm_columns.keys()[i]
            query += '  {},\n'.format(self.parse_column(column))

        query += '  {})\n'.format(self.detect_primary_key())

        return query

    def drop_table(self):
        """Return SQLite syntax for drop this model table
        """

        existance = config.Database().drop_table_behaviours.get(
            'drop_if_exists')

        query = 'DROP TABLE {}{}'.format(
            'IF EXISTS ' if existance else '',
            self.model.__storm_table__
        )

        return query

    @staticmethod
    def register():
        """Register this component
        """

        try:
            components.registerAdapter(MambaSQLAdapter, SQLite, IMambaSQL)
        except ValueError:
            # component already registered
            pass
