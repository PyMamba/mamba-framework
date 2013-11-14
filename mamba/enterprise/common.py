# -*- test-case-name: mamba.test.test_database -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: sqlite_adapter
    :platform: Unix, Windows
    :synopsis: SQLite adapter for create SQLite tables

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

from storm.expr import Undef
from storm import variables, properties
from storm.locals import create_database, Store

from mamba.utils import config


class NativeEnumVariable(variables.Variable):
    __slots__ = ("_set")

    def __init__(self, _set, *args, **kwargs):
        self._set = _set
        variables.Variable.__init__(self, *args, **kwargs)

    def parse_set(self, value, from_db):
        if from_db:
            return value

        return self._parse_common(value)

    def parse_get(self, value, to_db):
        if to_db:
            return value

        return self._parse_common(value)

    def _parse_common(self, value):
        if value not in self._set:
            raise ValueError("Invalid enum value: {}".format(value))

        return value


class NativeEnum(properties.SimpleProperty):
    """
    Enumeration property, allowing the use of native enum types in MySQL
    and PostgreSQL.

    For instance::

        class Class(Storm):
            prop = NativeEnum(set={'one', 'two'})

        obj.prop = "one"
        assert obj.prop == "one"

        obj.prop = 1 # Raises error.
    """

    variable_class = NativeEnumVariable

    def __init__(self, name=None, primary=False, **kwargs):
        _set = set(kwargs.pop('set'))
        kwargs['_set'] = _set

        properties.SimpleProperty.__init__(self, name, primary, **kwargs)


class CommonSQL(object):
    """I do nothing, my only purpose is serve as dummy object
    """

    def insert_data(self):
        """
        Return the SQL syntax needed to insert the data already present
        in the table.
        """

        store = Store(create_database(config.Database().uri))
        registers = []
        rows = store.find(self.model.__class__)
        fields = [
            r._detect_attr_name(self.model.__class__) for r in
            self.model._storm_columns.keys()
        ]
        for r in rows:
            tmp_row = {}
            for field in fields:
                tmp_row[field] = getattr(r, field)
            registers.append(tmp_row)

        if self.__class__.__name__ == 'MySQL':
            commas = '`'
        else:
            commas = "'"

        query = ''
        for register in registers:
            query += ('INSERT INTO {}{}{} ({}) VALUES ({});\n'.format(
                commas,
                self.model.__storm_table__,
                commas,
                ', '.join(register.keys()),
                ', '.join([(
                    str(field) if type(field) is not unicode
                    else "'{}'".format(field))
                    for field in register.values()
                ])
            ))

        return query

    def _parse_float(self, column):
        """
        Parse an specific floating point type for MySQL/Postgres, for example:

            double precession

        :param column: the Storm properties column to parse
        :type column: :class:`storm.properties.Float`
        """

        if column.__class__.__name__ == 'Float':
            column_type = 'real'
        else:
            column_type = 'double precission'

        return column_type

    def _parse_unicode(self, column):
        """
        Parse an specific floating point type for MySQL/Postgres, for example:

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
            return ' default {}'.format(variable._value)

        return ''

    def is_compound_key(self, name):
        """Detects if given name is part of a compound primary key

        :returns: `bool`
        """
        if hasattr(self.model, '__storm_primary__'):
            return name in self.model.__storm_primary__

        return False

    def get_storm_columns(self):
        return self.model._storm_columns.items()

    def get_single_primary_key(self):
        for column, property_ in self.get_storm_columns():
            if property_.primary == 1:
                return (column, property_)

    def get_compound_primary_key(self):
        primary_key_names = self.model.__storm_primary__
        primary_key_list = []

        for column, property_ in self.get_storm_columns():
            if property_.name in primary_key_names:
                primary_key_list.append(column)

        primary_key_list.sort()

        return primary_key_list

    def get_primary_key_columns(self):
        """Return one or more primary key column(s)
        """
        if not hasattr(self.model, '__storm_primary__'):
            return (self.get_single_primary_key()[0], )

        return self.get_compound_primary_key()

    def get_primary_key_names(self):
        """Return one or more primary key name(s)
        """
        if hasattr(self.model, '__storm_primary__'):
            return self.model.__storm_primary__
        else:
            primary_key = self.get_single_primary_key()
            if primary_key is not None:
                return (primary_key[1].name, )

        return None