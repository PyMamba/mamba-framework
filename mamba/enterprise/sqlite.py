# -*- test-case-name: mamba.test.test_model -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: sqlite_adapter
    :platform: Unix, Windows
    :synopsis: SQLite adapter for create SQLite tables

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

import inspect
from sqlite3 import sqlite_version_info

from storm import properties
from twisted.python import components
from storm.references import Reference
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
        """
        Get all the :class:`storm.references.Reference` and create foreign
        keys for the SQL creation script if the SQLite version is equal or
        better than 3.6.19

        If we are using references we should define our classes in a
        correct way. If we have a model that have a relation of many
        to one, we should define a many-to-one Storm relationship in
        that object but we must create a one-to-many relation in the
        related model. That means if for example we have a `Customer`
        model and an `Adress` model and we need to relate them as
        one Customer may have several addresses (in a real application
        address may have a relation many-to-many with customer) we
        should define a relation with `Reference` from Address to
        Customer using a property like `Address.customer_id` and a
        `ReferenceSet` from `Customer` to `Address` like:

            Customer.addresses = ReferenceSet(Customer.id, Address.id)

        In the case of many-to-many relationships, mamba create the
        relation tables by itself so you dont need to take care of
        yourself.

        .. warning:

            If you need a many2many relation you
            should add a Reference for the compound primary key in the
            relation table
        """

        if sqlite_version_info < (3, 6, 19):
            return

        references = []
        for attr in inspect.classify_class_attrs(self.model.__class__):

            if type(attr.object) is Reference:
                relation = attr.object._relation
                keys = {
                    'remote': relation.remote_key,
                    'local': relation.local_key
                }
                remote_table = relation.remote_cls.__storm_table__

                localkeys = ', '.join(k.name for k in keys.get('local'))
                remotekeys = ', '.join(k.name for k in keys.get('remote'))

                query = (
                    'FOREIGN KEY({localkeys}) REFERENCES {remote_table}('
                    '{remotekeys}) ON DELETE {on_delete} ON UPDATE '
                    '{on_update}'.format(
                        remote_table=remote_table,
                        localkeys=localkeys,
                        remotekeys=remotekeys,
                        on_update=getattr(
                            self.model, '__on_update__', 'NO ACTION'),
                        on_delete=getattr(
                            self.model, '__on_delete__', 'NO ACTION')
                    )
                )
                references.append(query)

        return ', '.join(references)

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
        query += '  {}'.format(self.detect_primary_key())
        query += '{}'.format(
            ', {}\n'.format(self.parse_references()) if self.parse_references()
            else ''
        )
        query += '\n);\n'

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
