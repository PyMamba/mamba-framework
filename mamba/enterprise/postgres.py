# -*- test-case-name: mamba.test.test_database -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: postgres_adapter
    :platform: Unix, Windows
    :synopsis: PostgreSQL adapter for create SQLite tables

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

import sys
import inspect

from storm import variables
from twisted.python import components
from storm.references import Reference

from mamba.utils import config
from mamba.core.interfaces import IMambaSQL
from mamba.enterprise.common import CommonSQL
from mamba.core.adapters import MambaSQLAdapter


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
        if '__pypy__' in sys.modules:
            # try to use psycopg2ct if we are on PyPy
            try:
                from psycopg2ct import compat
                compat.register()

                # monkey patch to dont let Storm crash on register type
                import psycopg2
                psycopg2._psycopg = object

                class _psycopg:
                    UNICODEARRAY = psycopg2.extensions.UNICODEARRAY

                from twisted.python.monkey import MonkeyPatcher
                monkey_patcher = MonkeyPatcher(
                    (psycopg2, '_psycopg', _psycopg))
                monkey_patcher.patch()

            except ImportError:
                raise RuntimeError(
                    'You are trying to use PostgreSQL with PyPy. Regular '
                    'psycopg2 module don\'t work with PyPy, you may install '
                    'psycoph2ct in order to can use psycopg2 with PyPy'
                )

        self.model = model

    def parse_references(self):
        """
        Get all the :class:`storm.references.Reference` and create foreign
        keys for the SQL creation script

        .. warning:

            If you need a many2many relation you
            should add a Reference for the compound primary key in the
            relation table
        """

        references = []
        for attr in inspect.classify_class_attrs(self.model.__class__):

            if type(attr.object) is Reference:
                relation = attr.object._relation
                keys = {
                    'remote': relation.remote_key[0],
                    'local': relation.local_key[0]
                }
                remote_table = relation.remote_cls.__storm_table__

                query = (
                    'CONSTRAINT {remote_table}_ind FOREIGN KEY ({localkey}) '
                    'REFERENCES {remote_table}({id}) '
                    'ON UPDATE {on_update} ON DELETE {on_delete}'.format(
                        remote_table=remote_table,
                        localkey=keys.get('local').name,
                        id=keys.get('remote').name,
                        on_update=getattr(
                            self.model, '__on_update__', 'RESTRICT'),
                        on_delete=getattr(
                            self.model, '__on_delete__', 'RESTRICT')
                    )
                )
                references.append(query)

        return ', '.join(references)

    def parse_column(self, column):
        """
        Parse a Storm column to the correct PostgreSQL value type. For example,
        if we pass a column of type :class:`storm.variable.IntVariable` with
        name `amount` we get back:

            'amount' integer

        :param column: the Storm properties column to parse
        :type column: :class:`storm.properties`
        """

        if column.variable_class is variables.IntVariable:
            column_type = self._parse_int(column)
        elif column.variable_class is variables.BoolVariable:
            column_type = 'bool'
        elif column.variable_class is variables.DecimalVariable:
            column_type = 'decimal'
        elif column.variable_class is variables.FloatVariable:
            column_type = self._parse_float(column)
        elif column.variable_class is variables.UnicodeVariable:
            column_type = self._parse_unicode(column)
        elif column.variable_class is variables.UUIDVariable:
            column_type = 'uuid'
        elif column.variable_class is variables.RawStrVariable:
            column_type = 'bytea'
        elif column.variable_class is variables.PickleVariable:
            column_type = 'bytea'
        elif column.variable_class is variables.JSONVariable:
            column_type = 'json'
        elif column.variable_class is variables.DateTimeVariable:
            column_type = 'timestamp'
        elif column.variable_class is variables.DateVariable:
            column_type = 'date'
        elif column.variable_class is variables.TimeVariable:
            column_type = 'time'
        elif column.variable_class is variables.TimeDeltaVariable:
            column_type = 'interval'
        elif column.variable_class is variables.ListVariable:
            column_type = self._parse_list(column)
        elif column.variable_class is variables.EnumVariable:
            column_type = 'enum_'
            column_type += column._detect_attr_name(self.model.__class__)
        else:
            column_type = 'text'  # fallback to text (tears are comming)

        column_type = '{} {}{}{}'.format(
            column._detect_attr_name(self.model.__class__),
            column_type,
            self._null_allowed(column),
            self._default(column)
        )
        return column_type

    def parse_enum(self, column):
        """
        Parses an enumeration column type. In PostgreSQL enumerations are
        created using ``CREATE TYPE <name> AS ENUM (<values>);`` format so
        we need to parse it separeted from regular column parsing.

        :param column: the Storm properties column to parse
        :type column: :class:`storm.properties`
        """

        if column.variable_class is not variables.EnumVariable:
            raise PostgreSQLNotEnumColumn(
                'Column {} is not an Enum column'.format(column)
            )

        data = column._variable_kwargs.get('get_map', {})
        return 'CREATE TYPE {} AS ENUM {};'.format(
            'enum_{}'.format(column._detect_attr_name(self.model.__class__)),
            '({})'.format(
                ', '.join("'{}'".format(
                    data[i]) for i in range(1, len(data) + 1)
                )
            )
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

        if not hasattr(self.model, '__storm_primary__'):
            for column in self.model._storm_columns.values():
                if column.primary == 1:
                    return 'CONSTRAINT {} PRIMARY KEY({})'.format(
                        self.model.__storm_table__ + '_pkey',
                        column.name
                    )

            raise PostgreSQLMissingPrimaryKey(
                'PostgreSQL based model {} is missing a primary '
                'key column'.format(repr(self.model))
            )

        return 'CONSTRAINT {} PRIMARY KEY {}'.format(
            self.model.__storm_table__ + '_pkey',
            str(self.model.__storm_primary__)
        )

    def create_table(self):
        """Return the PostgreSQL syntax for create a table with this model
        """

        enums = []
        query = 'CREATE TABLE {} (\n'.format((
            'IF NOT EXISTS {}'.format(self.model.__storm_table__) if (
            config.Database().create_table_behaviours.get(
                'create_if_not_exists'))
            else self.model.__storm_table__
        ))
        for i in range(len(self.model._storm_columns.keys())):
            column = self.model._storm_columns.keys()[i]
            if column.variable_class is not variables.EnumVariable:
                query += '  {},\n'.format(self.parse_column(column))
            else:
                enums.append(self.parse_enum(column))
                query += '  {},\n'.format(self.parse_column(column))

        query += '  {}\n'.format(self.detect_primary_key())
        query += '{}'.format(
            ', {}\n);'.format(
            self.parse_references()) if self.parse_references()
            else '\n);\n'
        )
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
            'drop_if_exists')
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
            if column_name.lower() == 'smallint':
                column_name = 'smallserial'
            elif column_name.lower() == 'bigint':
                column_name = 'bigserial'
            else:
                column_name = 'serial'

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

    @staticmethod
    def register():
        """Register this component
        """

        try:
            components.registerAdapter(MambaSQLAdapter, PostgreSQL, IMambaSQL)
        except ValueError:
            # component already registered
            pass
