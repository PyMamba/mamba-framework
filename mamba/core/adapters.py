
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: adapters
    :platform: Unix, Windows
    :synopsys: Component Adapters

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

from storm.info import get_obj_info
from zope.interface import implements

from mamba.core.interfaces import IMambaSQL


class MambaSQLAdapter:

    implements(IMambaSQL)

    def __init__(self, original):
        self.original = original

        if not hasattr(self.original.model, '_storm_columns'):
            get_obj_info(self.original.model)

    def parse_column(self, column):
        """Parse a Storm column to the correct SQL value
        """

        return self.original.parse_column(column)

    def detect_primary_key(self):
        """Detect and reeturn the primary key for the table
        """

        return self.original.detect_primary_key()

    def create_table(self):
        """
        Return the SQL syntax string to create a table to the selected
        underlying database system
        """

        return self.original.create_table()

    def drop_table(self):
        """
        Return the SQL syntax string to drop a table from the selected
        underlying database system
        """

        return self.original.drop_table()

    def insert_data(self, scheme):
        """Return the SQL syntax string to insert data that populate a table
        """

        return self.original.insert_data(scheme)

    def parse_references(self):
        """Return the SQL syntax to create foreign keys for PostgreSQL
        """

        return self.original.parse_references()

    def parse_indexes(self):
        """Return the SQL syntax to create indexes for PostgreSQL or SQLite
        """

        return self.original.parse_indexes()
