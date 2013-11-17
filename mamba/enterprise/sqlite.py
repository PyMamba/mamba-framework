# -*- test-case-name: mamba.test.test_model -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: sqlite_adapter
    :platform: Unix, Windows
    :synopsis: SQLite adapter for create SQLite tables

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

from storm import properties
from twisted.python import components
from singledispatch import singledispatch

from mamba.utils import config
from mamba.core.interfaces import IMambaSQL
from mamba.core.adapters import MambaSQLAdapter
from mamba.enterprise.common import CommonSQL, NativeEnum


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

        self._columns_mapping = {
            properties.Enum: 'integer',
            properties.Bool: 'integer',
            properties.Int: 'integer',
            properties.RawStr: 'blob',
            properties.Pickle: 'blob',
            properties.JSON: 'blob',
            properties.Float: 'real',
            properties.Unicode: 'varchar',
            properties.DateVariable: 'varchar',
            properties.DateTimeVariable: 'varchar',
            properties.TimeVariable: 'varchar',
            properties.TimeDeltaVariable: 'varchar',
            properties.ListVariable: 'varchar',
            NativeEnum: 'varchar'
        }

        self.parse = singledispatch(self.parse)

    def parse_references(self):
        """Just skips because SQLite doen't know anything about foreign keys
        """
        pass

    def parse_column(self, column):
        """
        Parse a Storm column to the correct SQLite value type. For example,
        if we pass a column of type :class:`storm.variable.IntVariable` with
        name `amount` we get back:

            amount integer

        :param column: the Storm properties column to parse
        :type column: :class:`storm.properties`
        """

        column_type = '{} {}{}{}{}'.format(
            column._detect_attr_name(self.model.__class__),
            self.parse(column),
            self._null_allowed(column),
            self._default(column),
            self._unique(column)
        )
        return column_type

    def parse(self, column):
        """This funciton is just a fallback to text (tears are comming)
        """

        return self._columns_mapping.get(column.__class__, 'text')

    def _unique(self, column):
        """
        Parse the column to check if a column is Unique

        :param column: the Storm properties column to parse
        :type column: :class:`storm.properties.Property`
        """
        wrap_column = column._get_column(self.model.__class__)
        return ' UNIQUE' if wrap_column.unique else ''

    def parse_indexes(self):
        indexes = []
        indexes.extend(self.get_single_indexes())
        indexes.extend(self.get_compound_indexes())

        return '\n'.join(indexes)

    def get_single_indexes(self):
        indexes = []

        for column, property_ in self.get_storm_columns():
            wrap_column = column._get_column(self.model.__class__)

            if not wrap_column.index:
                continue

            query = (
                'CREATE INDEX {}_ind ON {} ({});'.format(
                    property_.name,
                    self.model.__storm_table__,
                    property_.name
                )
            )
            indexes.append(query)

        return indexes

    def get_compound_indexes(self):
        """Checks if the model has an __mamba_index__ property.
        If so, we create a compound index with the fields specified inside
        __mamba_index__. This variable must be a tuple of tuples.

        Example: (
            ('field1', 'field2'),
            ('field3', 'field4', 'field5')
        )
        """
        compound_indexes = getattr(self.model, '__mamba_index__', None)

        if compound_indexes is None:
            return []

        compound_query = []
        for compound in compound_indexes:
            query = (
                'CREATE INDEX {}_ind ON {} ({});'.format(
                    '_'.join(compound),
                    self.model.__storm_table__,
                    ', '.join([c for c in compound])
                )
            )

            compound_query.append(query)

        return compound_query

    def detect_uniques(self):
        """Checks if the model has an __mamba_unique__ property.
        If so, we create a compound unique with the fields specified inside
        __mamba_unique__. This variable must be a tuple of tuples.

        Example: (
            ('field1', 'field2'),
            ('field3', 'field4', 'field5')
        )
        """
        compound_uniques = getattr(self.model, '__mamba_unique__', None)

        if compound_uniques is None:
            return ''

        compound_query = []
        for compound in compound_uniques:
            query = 'UNIQUE ({})'.format(
                ', '.join(compound)
            )
            compound_query.append(query)

        return ', '.join(compound_query)

    def detect_primary_key(self):
        """
        Detect the primary key for the model and return it back with the
        correct SQLite syntax

        :returns: a string with the correct SQLite syntax
        :rtype: str
        :raises: SQLiteMissingPrimaryKey on missing primary key
        """

        primary_key = self.get_primary_key_names()

        if primary_key is None:
            raise SQLiteMissingPrimaryKey(
                'SQLite based model {} is missing a primary key column'.format(
                    repr(self.model)
                )
            )

        return 'PRIMARY KEY({})'.format(', '.join(primary_key))

    def create_table(self):
        """Return the SQLite syntax for create a table with this model
        """

        query = 'CREATE TABLE {} (\n'.format((
            'IF NOT EXISTS {}'.format(self.model.__storm_table__) if (
                config.Database().create_table_behaviours.get(
                    'create_table_if_not_exists'))
            else self.model.__storm_table__
        ))

        primary_keys = self.get_primary_key_columns()

        if primary_keys is not None:
            for pk in primary_keys:
                query += '  {},\n'.format(self.parse_column(pk))

        for column, property_ in self.get_storm_columns():
            if property_.primary == 1 or self.is_compound_key(property_.name):
                continue
            query += '  {},\n'.format(self.parse_column(column))

        query += '{}'.format(
            '{},'.format(self.detect_uniques()) if self.detect_uniques()
            else ''
        )
        query += '  {}\n);\n'.format(self.detect_primary_key())

        if (config.Database().create_table_behaviours.get('drop_table')
            and not config.Database().create_table_behaviours.get(
                'create_if_not_exists')):
            query = '{};\n{}'.format(
                self.drop_table(),
                query
            )

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
