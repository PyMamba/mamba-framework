# -*- test-case-name: mamba.test.test_database -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: sqlite_adapter
    :platform: Unix, Windows
    :synopsis: SQLite adapter for create SQLite tables

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

from storm import properties


class SmallInt(properties.Int):
    """
    This class is a Storm extension of the MySQL and PostgreSQL numeric
    type used to store values in two bytes.

    Storm only uses the Int property type to store all kind of numeric data.
    This is a correct behaviour because Storm is a schemaless ORM but we
    need to know which exact weight we are going to use for a field because
    we generate the database using the model.
    """
    pass


class BigInt(properties.Int):
    """
    This class is a Storm extension of the MySQL and PostgreSQL numeric
    type used to store values in four bytes.

    Storm only uses the Int property type to store all kind of numeric data.
    This is a correct behaviour because Storm is a schemaless ORM but we
    need to know which exact weight we are going to use for a field because
    we generate the database using the model.
    """
    pass


class DoublePrecission(properties.Float):
    """
    This class is a Storm extension of the MySQL and PostgreSQL floating type
    used to store approximate values in eigth bytes.

    Storm only uses the Int property type to store all kind of numeric data.
    This is a correct behaviour because Storm is a schemaless ORM but we
    need to know which exact weight we are going to use for a field because
    we generate the database using the model.
    """
    pass


class DummySQL:
    """I do nothing, my only purpse is serve as dummy object"""

    def __init__(self, model):
        self.model = model
