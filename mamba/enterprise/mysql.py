# -*- test-case-name: mamba.test.test_database -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: mysql_adapter
    :platform: Unix, Windows
    :synopsis: MySQL adapter for create MySQL tables

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

import inspect

from storm.expr import Undef
from twisted.python import components
from storm.references import Reference
from storm import variables, properties
from singledispatch import singledispatch

from mamba.utils import config
from mamba.core.interfaces import IMambaSQL
from mamba.core.adapters import MambaSQLAdapter
from mamba.enterprise.common import CommonSQL, NativeEnumVariable, NativeEnum


class MySQLError(Exception):
    """Base class for MySQL related exceptions
    """


class MySQLMissingPrimaryKey(MySQLError):
    """Fired when the model is missing the primary key
    """


class MySQLNotEnumColumn(MySQLError):
    """Fired when parse_enum is called with a column that is not an Enum
    """


class MySQL(CommonSQL):
    """
    This class implements the MySQL syntax layer for mamba

    :param module: the module to generate MySQL syntax for
    :type module: :class:`~mamba.Model`
    """

    def __init__(self, model):
        self.model = model

        self._columns_mapping = {
            properties.Bool: 'tinyint',
            properties.UUID: 'blob',
            properties.RawStr: 'blob',
            properties.Pickle: 'varbinary',
            properties.JSON: 'blob',
            properties.DateTime: 'datetime',
            properties.Date: 'date',
            properties.Time: 'time',
            properties.Enum: 'integer',
            NativeEnum: 'enum'
        }

        self.parse = singledispatch(self.parse)
        self.parse.register(properties.Int, self.parse_int)
        self.parse.register(properties.Decimal, self.parse_decimal)
        self.parse.register(properties.Unicode, self._parse_unicode)
        self.parse.register(properties.Float, self._parse_float)

    @property
    def engine(self):
        """
        Return back the type of engine defined for this MySQL table, if
        no engnine has been configured use InnoDB as default
        """

        if not hasattr(self.model, '__engine__'):
            return 'InnoDB'

        return self.model.__engine__

    @staticmethod
    def register():
        """Register this component
        """

        try:
            components.registerAdapter(MambaSQLAdapter, MySQL, IMambaSQL)
        except ValueError:
            # component already registered
            pass

    def get_single_indexes(self):
        """Goes through every field looking for an index parameter.
        """
        single_query = []
        for column, property_ in self.get_storm_columns():
            wrap_column = column._get_column(self.model.__class__)
            index = wrap_column.index
            unique = wrap_column.unique

            if unique:
                # We already have a index for this column, so move on.
                continue

            if index:
                query = 'INDEX `{}_ind` (`{}`)'.format(
                    property_.name,
                    property_.name
                    )
                single_query.append(query)

        return single_query

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
            query = 'INDEX `{}_ind` ({})'.format(
                '_'.join(compound),
                ', '.join(['`{}`'.format(c) for c in compound])
            )

            compound_query.append(query)

        return compound_query

    def detect_indexes(self):
        """
        Go through all the fields defined in the model and create a index
        constraint if the index property is set on the field.
        """
        indexes = []
        indexes.extend(self.get_single_indexes())
        indexes.extend(self.get_compound_indexes())

        return ', '.join(indexes)

    def get_single_uniques(self):
        """Goes through every field looking for an unique parameter.
        """
        single_query = []
        for column, property_ in self.get_storm_columns():
            wrap_column = column._get_column(self.model.__class__)
            unique = wrap_column.unique

            if unique:
                query = 'UNIQUE `{}_uni` (`{}`)'.format(
                    property_.name,
                    property_.name
                    )
                single_query.append(query)

        return single_query

    def get_compound_uniques(self):
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
            return []

        compound_query = []
        for compound in compound_uniques:
            query = 'UNIQUE `{}_uni` ({})'.format(
                '_'.join(compound),
                ', '.join(['`{}`'.format(c) for c in compound])
            )

            compound_query.append(query)

        return compound_query

    def detect_uniques(self):
        """
        Go through all the fields defined in the model and create a unique
        key if the unique property is set on the field.
        """
        uniques = []
        uniques.extend(self.get_single_uniques())
        uniques.extend(self.get_compound_uniques())

        return ', '.join(uniques)

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

            If no InnoDB is used as engine in MySQL then this is skipped.
            :class:`storm.references.ReferenceSet` does not generate
            foreign keys by itself. If you need a many2many relation you
            should add a Reference for the compound primary key in the
            relation table
        """

        if self.engine != 'InnoDB':
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

                localkeys = ', '.join(
                    '`{}`'.format(k.name) for k in keys.get('local')
                )
                remotekeys = ', '.join(
                    '`{}`'.format(k.name) for k in keys.get('remote')
                )

                query = (
                    'INDEX `{remote_table}_fk_ind` ({localkeys}), FOREIGN KEY '
                    '({localkeys}) REFERENCES `{remote_table}`({remotekeys}) '
                    'ON UPDATE {on_update} ON DELETE {on_delete}'.format(
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

        return ', '.join(references)

    def parse(self, column):
        """This function is just a fallback to text (tears are comming)
        """

        return self._columns_mapping.get(column.__class__, 'text')

    def parse_int(self, column):
        """
        Parse an specific integer type for MySQL, for example:

            smallint UNSIGNED

        :param column: the Storm properties column to parse
        :type column: :class:`storm.properties.Int`
        """

        column_name = column.__class__.__name__
        wrap_column = column._get_column(self.model.__class__)
        auto_increment = wrap_column.auto_increment
        unsigned = wrap_column.unsigned
        size = wrap_column.size

        return '{}{}{}'.format(
            '{}{}'.format(
                column_name.lower(),
                '({})'.format(size) if size is not Undef else ''
            ),
            ' UNSIGNED' if unsigned else '',
            ' AUTO_INCREMENT' if auto_increment else ''
        )

    def parse_decimal(self, column):
        """Parse decimal sizes for MySQL, for example:

            decimal(10,2)

        :param column: the Storm properties column to parse
        :type column: :class:`storm.properties.Decimal`
        """

        column_name = column.__class__.__name__
        wrap_column = column._get_column(self.model.__class__)
        size = wrap_column.size

        parsed_size = parse_decimal_size(size, column_name)
        if type(parsed_size) is not tuple:
            return parsed_size

        return '{}{}'.format(
            column_name.lower(), '({},{})'.format(
                *parse_decimal_size(size, column_name))
        )

    def parse_column(self, column):
        """
        Parse a Storm column to the correct MySQL value type. For example,
        if we pass a column of type :class:`~mamba.variable.SmallIntVariable`
        with name `amount` we get back:

            `amount` smallint

        :param column: the Storm properties column to parse
        :type column: :class:`storm.properties`
        """

        column_type = '`{}` {}{}{}'.format(
            column._detect_attr_name(self.model.__class__),
            self.parse(column),
            self._null_allowed(column),
            self._default(column)
        )
        return column_type

    def parse_enum(self, column):
        """Parse an enum column
        """

        if column.variable_class is not NativeEnumVariable:
            raise MySQLNotEnumColumn(
                'Column {} is not an Enum column'.format(column)
            )

        data = column._variable_kwargs.get('_set', set())

        return '`{}` enum({})'.format(
            column._detect_attr_name(self.model.__class__),
            ', '.join("'{}'".format(i) for i in data)
        )

    def detect_primary_key(self):
        """
        Detect the primary key for the model and return it back with the
        correct MySQL syntax, Example:

            PRIMARY KEY(`id`)

        :returns: a string with the correct MySQL syntax
        :rtype: str
        :raises: MySQLMissingPrimaryKey on missing primary key
        """
        primary_key = self.get_primary_key_names()

        if primary_key is None:
            raise MySQLMissingPrimaryKey(
                'MySQL based model {} is missing a primary key column'.format(
                    repr(self.model)
                )
            )

        primary_key_str = ', '.join(['`{}`'.format(c) for c in primary_key])

        return 'PRIMARY KEY({})'.format(primary_key_str)

    def create_table(self):
        """Return the MySQL syntax for create a table with this model
        """

        query = 'CREATE TABLE {} (\n'.format((
            'IF NOT EXISTS `{}`'.format(self.model.__storm_table__) if (
                config.Database().create_table_behaviours.get(
                    'create_table_if_not_exists'))
            else '`' + self.model.__storm_table__ + '`'
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
                query += '  {},\n'.format(self.parse_enum(column))

        query += '  {}\n'.format(self.detect_primary_key())
        query += '{}'.format(
            ', {}'.format(self.detect_uniques()) if self.detect_uniques()
            else ''
        )
        query += '{}'.format(
            ', {}'.format(self.detect_indexes()) if self.detect_indexes()
            else ''
        )
        query += '{}'.format(
            ', {}'.format(self.parse_references()) if self.parse_references()
            else ''
        )
        query += '\n) ENGINE={} DEFAULT CHARSET=utf8;\n'.format(self.engine)

        if (config.Database().create_table_behaviours.get('drop_table')
            and not config.Database().create_table_behaviours.get(
                'create_if_not_exists')):
            query = '{};\n{}'.format(
                self.drop_table(),
                query
            )

        return query

    def drop_table(self):
        """Return MySQL syntax for drop this model table
        """

        existance = config.Database().drop_table_behaviours.get(
            'drop_if_exists')

        query = 'DROP TABLE {}`{}`'.format(
            'IF EXISTS ' if existance else '',
            self.model.__storm_table__
        )

        return query

    def _default(self, column):
        """
        Get the default argument for a column (if any)

        :param column: the Storm properties column to parse
        :type column: :class:`storm.properties.Property`
        """

        property_column = column._get_column(self.model.__class__)
        variable = property_column.variable_factory()

        if type(variable._value) is bool:
            variable._value = int(variable._value)

        if variable._value is None:
            variable._value = 'NULL'

        if (column.variable_class is variables.DateTimeVariable
                or column.variable_class is variables.TimeVariable
                or column.variable_class is variables.DateVariable):
            if variable._value is not Undef:
                variable._value = "'" + str(variable._value) + "'"

        if variable._value is not Undef:
            return ' default {}'.format(variable._value)

        return ''


@singledispatch
def parse_decimal_size(size, column_name=None):
    """This is just a fallbacl for unknown decimal size type

    :param size: the given size
    :returns: tuple of (length, precission)
    """
    return column_name.lower()


@parse_decimal_size.register(list)
@parse_decimal_size.register(tuple)
def _parse_decimal_size_list(size, column_name=None):
    """Parse list decimal size
    """
    return size[0], size[1]


@parse_decimal_size.register(str)
def _parse_decimal_size_str(size, column_name=None):
    """Parse str decimal size
    """
    size = size.split(',')
    if len(size) == 1:
        return size[0], 2
    else:
        return size[0], size[1]


@parse_decimal_size.register(int)
def _parse_decimal_size_int(size, column_name=None):
    """Parse int decimal size
    """
    return size, 2


@parse_decimal_size.register(float)
def _parse_decimal_size_float(size, column_name=None):
    """Parse float decimal size
    """
    size = str(size).split('.')
    return size[0], size[1]
