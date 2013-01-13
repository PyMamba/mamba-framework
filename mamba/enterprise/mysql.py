# -*- test-case-name: mamba.test.test_database -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: mysql_adapter
    :platform: Unix, Windows
    :synopsis: MySQL adapter for create SQLite tables

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

import inspect

from storm.expr import Undef
from twisted.python import components
from storm.references import Reference
from storm import variables, properties

from mamba.utils import config
from mamba.core.interfaces import IMambaSQL
from mamba.enterprise.common import CommonSQL
from mamba.core.adapters import MambaSQLAdapter


class MySQLError(Exception):
    """Base class for MySQL related exceptions
    """


class MySQLMissingPrimaryKey(MySQLError):
    """Fired when the model is missing the primary key
    """


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


class MySQL(CommonSQL):
    """
    This class implements the MySQL syntax layer for mamba

    :param module: the module to generate MySQL syntax for
    :type module: :class:`~mamba.Model`
    """

    def __init__(self, model):
        self.model = model

    def parse_references(self):
        """
        Get all the :class:`storm.references.Reference` and create foreign
        keys for the SQL creation script

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
                    'remote': relation.remote_key[0],
                    'local': relation.local_key[0]
                }
                remote_table = relation.remote_cls.__storm_table__

                query = (
                    'INDEX `{remote_table}_ind` (`{localkey}`), FOREIGN KEY '
                    '(`{localkey}`) REFERENCES `{remote_table}`(`{id}`) '
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
        Parse a Storm column to the correct MySQL value type. For example,
        if we pass a column of type :class:`~mamba.variable.SmallIntVariable`
        with name `amount` we get back:

            `amount` smallint

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
        """Return the MySQL syntax for create a table with this model
        """

        query = 'CREATE TABLE {} (\n'.format((
            'IF NOT EXISTS `{}`'.format(self.model.__storm_table__) if (
            config.Database().create_table_behaviours.get(
                'create_if_not_exists'))
            else '`' + self.model.__storm_table__ + '`'
        ))

        for i in range(len(self.model._storm_columns.keys())):
            column = self.model._storm_columns.keys()[i]
            query += '  {},\n'.format(self.parse_column(column))

        query += '  {}\n'.format(self.detect_primary_key())
        query += '{}'.format(
            ', {}'.format(self.parse_references()) if self.parse_references()
            else ''
        )
        query += ') ENGINE={} DEFAULT CHARSET=utf8\n'.format(self.engine)

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

    def _parse_int(self, column):
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
