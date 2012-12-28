# -*- test-case-name: mamba.test.test_database -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: mysql_adapter
    :platform: Unix, Windows
    :synopsis: MySQL adapter for create SQLite tables

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

from storm.expr import Undef
from storm import variables, properties
from twisted.python import components

from mamba.core.interfaces import IMambaSQL
from mamba.core.adapters import MambaSQLAdapter
from mamba.enterprise.dummy import SmallInt, BigInt


class MySQLError(Exception):
    """Base class for MySQL related exceptions"""


class MySQLMissingPrimaryKey(MySQLError):
    """Fired when the model is missing the primary key"""


class TinyInt(properties.Int):
    """
    This class is a Storm extension of the MySQL numeric type used to store
    values in one byte.

    Storm only uses the Int property type to store all kind of numeric data.
    This is a correct behaviour because Storm is a schemaless ORM but we
    need to know which exact weight we are going to use for a field because
    we generate the database using the model.
    """
    pass


class MediumInt(properties.Int):
    """
    This class is a Storm extension of the MySQL numeric type used to store
    values in three bytes.

    Storm only uses the Int property type to store all kind of numeric data.
    This is a correct behaviour because Storm is a schemaless ORM but we
    need to know which exact weight we are going to use for a field because
    we generate the database using the model.
    """
    pass


class MySQL:
    """
    This class implements the MySQL syntax layer for mamba

    :param module: the module to generate MySQL syntax for
    :type module: :class:`~mamba.Model`
    """

    def __init__(self, model):
        self.model = model

    def parse_column(self, column):
        """
        Parse a Storm column to the correct MySQL value type. For example,
        if we pass a column of type :class:`storm.variable.IntVariable` with
        name `amount` we get back:

            amount SMALLINT

        :param column: the Storm properties column to parse
        :type column: :class:`storm.properties`
        """

        if column.variable_class is variables.IntVariable:
            column_type = self._parse_int(column)
        elif column.variable_class is variables.BoolVariable:
            column_type = 'tinyint'
        elif column.variable_class is variables.DecimalVariable:
            column_type = 'decimal'
        elif column.variable_class is variables.FloatVariable:
            column_type = self._parse_float(column)
        elif column.variable_class is variables.UnicodeVariable:
            column_type = self._parse_unicode(column)
        elif column.variable_class is variables.UUIDVariable:
            column_type = 'blob'
        elif column.variable_class is variables.RawStrVariable:
            # we don't care about different blob sizes
            column_type = 'blob'
        elif column.variable_class is variables.PickleVariable:
            # we don't care about different varbinary sizes
            column_type = 'varbinary'
        elif column.variable_class is variables.JSONVariable:
            column_type = 'blob'
        elif column.variable_class is variables.DateTimeVariable:
            column_type = 'datetime'
        elif column.variable_class is variables.DateVariable:
            column_type = 'date'
        elif column.variable_class is variables.TimeVariable:
            column_type = 'time'
        elif column.variable_class is variables.TimeDeltaVariable:
            column_type = 'text'
        elif column.variable_class is variables.EnumVariable:
            column_type = 'enum'
        else:
            column_type = 'text'  # fallback to text (tears are comming)

        column_type = '`{}` {}{}{}'.format(
            column._detect_attr_name(self.model.__class__),
            column_type,
            self._null_allowed(column),
            self._default(column)
        )
        return column_type

    def detect_primary_key(self):
        """
        Detect the primary key for the model and return it back with the
        correct MySQL syntax, Example:

            PRIMARY KEY(`id`)

        :returns: a string with the correct MySQL syntax
        :rtype: str
        :raises: MySQLMissingPrimaryKey on missing primary key
        """

        if not hasattr(self.model, '__storm_primary__'):
            for column in self.model._storm_columns.values():
                if column.primary == 1:
                    return 'PRIMARY KEY(`{}`)'.format(column.name)

            raise MySQLMissingPrimaryKey(
                'MySQL based model {} is missing a primary key column'.format(
                    repr(self.model)
                )
            )

        return 'PRIMARY KEY {}'.format(
            str(self.model.__storm_primary__).replace("'", "`")
        )

    def create_table(self):
        """
        Return the MySQL syntax for create a table with this model
        """

        query = 'CREATE TABLE `{}` (\n'.format(self.model.__storm_table__)
        for i in range(len(self.model._storm_columns.keys())):
            column = self.model._storm_columns.keys()[i]
            query += '  {},\n'.format(self.parse_column(column))

        query += '  {}\n'.format(self.detect_primary_key())
        # TODO: indexes and keys
        query += ') {} DEFAULT CHARSET=utf8\n'.format(
            self.engine
        )

        return query

    def _parse_int(self, column):
        """
        Parse an specific integer type for MySQL, for example:

            UNSIGNED SMALLINT

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

    def _parse_float(self, column):
        """
        Parse an specific floating point type for MySQL, for example:

            DOUBLE PRECISSION

        :param column: the Storm properties column to parse
        :type column: :class:`storm.properties.Float`
        """

        if column.__class__.__name__ == 'Float':
            column_type = 'float'
        else:
            column_type = 'double precission'

        return column_type

    def _parse_unicode(self, column):
        """
        Parse an specific floating point type for MySQL, for example:

            varchar(256)

        :param column: the Storm properties column to parse
        :type column: :class:`storm.properties.Unicode`
        """

        size = column._get_column(self.model.__class__).size

        return '{}{}'.format(
            'text' if size is Undef else 'varchar',
            '({})'.format(size) if size is not Undef else ''
        )

    def _null_allowed(self, column):
        """
        Parse the column to check if a column allows NULL values

        :param column: the Storm properties column to parse
        :type column: :class:`storm.properties.Property`
        """

        property_column = column._get_column(self.model.__class__)
        null_allowed = property_column.variable_factory()._allow_none

        return ' NOT NULL' if not null_allowed else ''

    def _default(self, column):
        """
        Get the default argument for a column (if any)

        :param column: the Storm properties column to parse
        :type column: :class:`storm.properties.Property`
        """

        property_column = column._get_column(self.model.__class__)
        variable = property_column.variable_factory()

        if variable._value is not Undef:
            return ' {}'.format(variable._value)

        return ''

    @property
    def engine(self):
        """
        Return back the type of engine defined for this MySQL table, if
        no engnine has been configured use InnoDB as default
        """

        if not hasattr(self.model, '__engine__'):
            return 'ENGINE=InnoDB'

        return 'ENGINE={}'.format(self.model.__engine__)

    @staticmethod
    def register():
        """Register this component"""

        components.registerAdapter(MambaSQLAdapter, MySQL, IMambaSQL)
