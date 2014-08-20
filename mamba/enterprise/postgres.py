# -*- test-case-name: mamba.test.test_database -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: postgres_adapter
    :platform: Unix, Windows
    :synopsis: PostgreSQL adapter for create PosetgreSQL tables

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

import inspect
from singledispatch import singledispatch

from twisted.python import components
from storm.references import Reference
from storm import properties, variables
from storm.expr import Undef, compile as storm_compile

from mamba.utils import config
from mamba.core.interfaces import IMambaSQL
from mamba.core.adapters import MambaSQLAdapter
from mamba.enterprise.common import CommonSQL, NativeEnum, NativeEnumVariable


class PostgreSQLError(Exception):
    """Base class for PostgreSQL errors
    """


class PostgreSQLMissingPrimaryKey(PostgreSQLError):
    """Fired when the model is missing the primary key
    """


class PostgreSQLMissingArrayDefinition(PostgreSQLError):
    """Fired when a List variable has no array definition
    """


class PostgreSQLNotEnumColumn(PostgreSQLError):
    """Fired when parse_enum is called with a column that is not an Enum
    """


class PostgreSQL(CommonSQL):
    """
    This class implements the PostgreSQL syntax layer for mamba

    :param module: the module to generate PostgreSQL syntax for
    :type module: :class:`~mamba.Model`
    """

    def __init__(self, model):

        self.model = model

        self._columns_mapping = {
            properties.Bool: 'bool',
            properties.UUID: 'uuid',
            properties.RawStr: 'bytea',
            properties.Pickle: 'bytea',
            properties.JSON: 'json',
            properties.DateTime: 'timestamp',
            properties.Date: 'date',
            properties.Time: 'time',
            properties.TimeDelta: 'interval',
            properties.Enum: 'integer',
            properties.Decimal: 'decimal'
        }

        self.parse = singledispatch(self.parse)
        self.parse.register(properties.Int, self._parse_int)
        self.parse.register(properties.Unicode, self._parse_unicode)
        self.parse.register(properties.Float, self._parse_float)
        self.parse.register(properties.List, self._parse_list)
        self.parse.register(NativeEnum, self._parse_enum)

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
                'CREATE INDEX {}_ind_{} ON {} ({});'.format(
                    property_.name,
                    self.model.__storm_table__,
                    self.model.__storm_table__,
                    self._parse_column_name(property_.name)
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
                'CREATE INDEX {}_ind_{} ON {} ({});'.format(
                    '_'.join(compound),
                    self.model.__storm_table__,
                    self.model.__storm_table__,
                    ', '.join([self._parse_column_name(c) for c in compound])
                )
            )

            compound_query.append(query)

        return compound_query

    def parse_references(self):
        """
        Get all the :class:`storm.references.Reference` and create foreign
        keys for the SQL creation script

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

        references = []
        for attr in inspect.classify_class_attrs(self.model.__class__):

            if type(attr.object) is Reference:
                relation = attr.object._relation

                if relation.on_remote is True:
                    # Don't create a FK for this as is defined on remote.
                    continue

                keys = {
                    'remote': relation.remote_key,
                    'local': relation.local_key
                }
                remote_table = relation.remote_cls.__storm_table__

                localkeys = ', '.join(k.name for k in keys.get('local'))
                remotekeys = ', '.join(k.name for k in keys.get('remote'))

                query = (
                    'ALTER TABLE {table} ADD '
                    'CONSTRAINT {field}_{remote_table}_ind FOREIGN KEY '
                    '({localkeys}) REFERENCES {remote_table}({remotekeys}) '
                    'ON UPDATE {on_update} ON DELETE {on_delete};\n'.format(
                        field=keys.get('local')[0].name,
                        table=self.model.__storm_table__,
                        remote_table=remote_table,
                        localkeys=localkeys,
                        remotekeys=remotekeys,
                        on_update=getattr(
                            self.model, '__on_update__', 'RESTRICT'),
                        on_delete=getattr(
                            self.model, '__on_delete__', 'RESTRICT')
                    )
                )
                references.append(query)

        return ''.join(references)

    def parse_column(self, column):
        """
        Parse a Storm column to the correct PostgreSQL value type. For example,
        if we pass a column of type :class:`storm.variable.IntVariable` with
        name `amount` we get back:

            'amount' integer

        :param column: the Storm properties column to parse
        :type column: :class:`storm.properties`
        """

        column_type = '"{}" {}{}{}{}'.format(
            column._detect_attr_name(self.model.__class__),
            self.parse(column),
            self._null_allowed(column),
            self._default(column),
            self._unique(column)
        )
        return column_type

    def parse(self, column):
        """This function is just a fallback to text (tears are comming)
        """

        return self._columns_mapping.get(column.__class__, 'text')

    def parse_enum(self, column):
        """
        Parses an enumeration column type. In PostgreSQL enumerations are
        created using ``CREATE TYPE <name> AS ENUM (<values>);`` format so
        we need to parse it separeted from regular column parsing.

        We have to add the table name to the enum name as we can't define
        more than one enum with the same name.

        :param column: the Storm properties column to parse
        :type column: :class:`storm.properties`
        """

        if column.variable_class is not NativeEnumVariable:
            raise PostgreSQLNotEnumColumn(
                'Column {} is not an Enum column'.format(column)
            )

        data = column._variable_kwargs.get('_set', set())
        return 'CREATE TYPE {} AS ENUM {};\n'.format(
            'enum_{}_{}'.format(
                column._detect_attr_name(self.model.__class__),
                self.model.__storm_table__
            ),
            '({})'.format(', '.join(["'{}'".format(i) for i in data]))
        )

    def detect_primary_key(self):
        """
        Detect the primary key for the model and return it back with the
        correct PostgreSQL syntax, Example:

            PRIMARY KEY('id')

        :returns: a string with the correct PostgreSQL syntax
        :rtype: str
        :raises: PostgreSQLMissingPrimaryKey on missing primary key
        """

        primary_key = self.get_primary_key_names()

        if primary_key is None:
            raise PostgreSQLMissingPrimaryKey(
                'PostgreSQL based model {} is missing a primary '
                'key column'.format(repr(self.model))
            )

        constraint = '{}_pkey'.format(self.model.__storm_table__)
        pkeys = ', '.join(primary_key)

        return 'CONSTRAINT {} PRIMARY KEY({})'.format(constraint, pkeys)

    def create_table(self):
        """Return the PostgreSQL syntax for create a table with this model
        """

        enums = []
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
            if column.variable_class is not NativeEnumVariable:
                query += '  {},\n'.format(self.parse_column(column))
            else:
                enums.append(self.parse_enum(column))
                query += '  {},\n'.format(self.parse_column(column))

        query += '{}'.format(
            '{},'.format(self.detect_uniques()) if self.detect_uniques()
            else ''
        )
        query += '  {}\n);\n'.format(self.detect_primary_key())
        query = ''.join(enums) + query

        if (config.Database().create_table_behaviours.get('drop_table')
            and not config.Database().create_table_behaviours.get(
                'create_if_not_exists')):
            query = '{};\n{}'.format(
                self.drop_table(),
                query
            )

        return query

    def drop_table(self):
        """Return PostgreSQL syntax for drop this model table
        """

        existance = config.Database().drop_table_behaviours.get(
            'drop_if_exists', True)
        restrict = config.Database().drop_table_behaviours.get(
            'restrict', True)
        cascade = config.Database().drop_table_behaviours.get('cascade', False)

        query = 'DROP TABLE {}{}{}{}'.format(
            'IF EXISTS ' if existance else '',
            self.model.__storm_table__,
            ' RESTRICT' if restrict else '',
            ' CASCADE' if cascade else ''
        )

        return query

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

    def _parse_int(self, column):
        """
        Parse an specific integer type for PostgreSQL, for example:

            bigserial

        .. admonition:: Notice

            If you use the ``unsigned=True`` param in the property definition
            mamba should ignore it at all. Only serial numeric types are
            unsigned in PostgreSQL and they are used for autoincrement

            Size param is also ignored when using Postgres as backend

            If you define ``auto_increment=True`` in the params of the
            property and you used the default ``Int`` or the mamba specials
            ``SmallInt``, ``BigInt`` then it will be automaticaly transformed
            to ``serial``, ``smallserial`` and ``bigserial`` respectively

        :param column: the Storm properties column to parse
        :type column: :class:`storm.properties.Int`
        """

        column_name = column.__class__.__name__
        wrap_column = column._get_column(self.model.__class__)
        auto_increment = wrap_column.auto_increment

        if auto_increment:
            column_mapping = {'smallint': 'smallserial', 'bigint': 'bigserial'}
            column_name = column_mapping.get(column_name.lower(), 'serial')

        return column_name.lower()

    def _parse_list(self, column):
        """
        Parse an array type for PostgreSQL.

        PostgreSQL allows columns of a table to be defined as variable-length
        multidimensional arrays. For example::

            squares integer[3][3]

        In the example above we create a multidimensional square variable using
        an integer type variable.

        We implement this using the mamba special property param 'array' that
        must be a string defining the PostgreSQL syntax on List, for example::

            squares = List(array='integer[3][3]')

        You can also use the alternative SQL standard compilant syntax::

            month integer ARRAY

        Lists can't be used with MySQL or SQLite backends

        seealso: http://www.postgresql.org/docs/9.2/static/arrays.html

        :param column: the Storm properties column to parse
        :type column: :class:`storm.properties.List`
        :raises: :class:`PostgreSQLMissingArrayDefinition` if the ``array``
                 param is not defined in the Property
        """

        wrap_column = column._get_column(self.model.__class__)
        array = wrap_column.array

        if array is None:
            raise PostgreSQLMissingArrayDefinition(
                'PostgreSQL based model {} is missing a array definition'
                'in a ListVariable argument {}'.format(
                    repr(self.model), repr(column)
                )
            )

        return array

    def _parse_enum(self, column):
        """Simple parse enum helper function
        """
        return 'enum_{}_{}'.format(
            column._detect_attr_name(self.model.__class__),
            self.model.__storm_table__
        )

    def _unique(self, column):
        """
        Parse the column to check if a column is Unique

        :param column: the Storm properties column to parse
        :type column: :class:`storm.properties.Property`
        """
        wrap_column = column._get_column(self.model.__class__)
        return ' UNIQUE' if wrap_column.unique else ''

    def _default(self, column):
        """
        Get the default argument for a column (if any)

        :param column: the Storm properties column to parse
        :type column: :class:`storm.properties.Property`
        """

        if column._variable_kwargs.get('value') is not Undef:
            property_column = column._get_column(self.model.__class__)
            variable = property_column.variable_factory()

            if type(variable._value) is bool:
                variable._value = 'TRUE' if variable._value else 'FALSE'

            if variable._value is None:
                variable._value = 'NULL'

            if (column.variable_class is variables.DateTimeVariable
                    or column.variable_class is variables.TimeVariable
                    or column.variable_class is variables.DateVariable
                    or column.variable_class is NativeEnumVariable):
                if variable._value is not Undef:
                    if variable._value != 'NULL':
                        variable._value = "'" + str(variable._value) + "'"

            if variable._value is not Undef:
                return ' default {}'.format(variable._value)

        return ''

    def _parse_column_name(self, column_name):
        """Parse a column name to make sure we quote resrerved words
        """

        if not storm_compile.is_reserved_word(column_name):
            return column_name

        return '"{}"'.format(column_name.replace('"', '""'))

    @staticmethod
    def register():
        """Register this component
        """

        try:
            components.registerAdapter(MambaSQLAdapter, PostgreSQL, IMambaSQL)
        except ValueError:
            # component already registered
            pass
