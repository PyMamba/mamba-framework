.. _model:

=====================
The mamba model guide
=====================

Mamba doesn't use any type of configuration file to generate database schemas, in mamba the schema is defined in Python classes directly extending the :class:`mamba.application.model.Model` class.

Creating a new model
====================

We can generate new model classes using the ``mamba-admin`` command line tool or adding a new file with a class that inherits from :class:`mamba.application.model.Model` directly. If you use the command line, you have pass two arguments at least, the model name and the real database table that is related to::

    $ mamba-admin model dummy dummy_table

The command above will create a new ``dummy.py`` file in the ``application/model`` directory with the following content:

.. sourcecode:: python

    # -*- encoding: utf-8 -*-
    # -*- mamba-file-type: mamba-model -*-
    # Copyright (c) 2013 - user <user@localhost>

    """
    .. model:: Dummy
        :plarform: Linux
        :synopsis: None
    .. modelauthor:: user <user@localhost>
    """

    from storm.locals import Int
    from mamba.application import model


    class Dummy(model.Model):
        """
        None
        """

        __storm_table__ = 'dummy_table'
        id = Int(primary=True, unsigned=True)

You can pass so many parameters to the ``mamba-admin model`` subcommand for example to set the description of the model, the author name and email, the platforms that this model is compatible with and the classname you want for your model.

As you can see in the code that ``mamba-admin`` tool generated for us, we define a new class ``Dummy`` that inherits from :class:`mamba.application.model.Model` class and define a static property named ``__storm_table__`` that points to the real name of our database table, ``dummy_table`` in this case. The class define another static property ``id`` that is an instance of the |storm|_ class :class:`storm.properties.Int` with the parameters ``primary`` and ``unsigned`` as ``True``.

Mamba's Storm properties
------------------------
In mamba we define our databse schema just creating new Python classes like the one in the example, the following is a table of the available |storm| types and their SQLite, MySQL/MariaDB and PostgreSQL equivalents:

+------------+-----------+---------------------+-------------------------------------------+-------------------------------------------------------+
| Property   | Python    | SQLite              | MySQL/MariaDB                             | PostgreSQL                                            |
+============+===========+=====================+===========================================+=======================================================+
| Bool       | bool      | INT                 | TINYINT                                   | BOOL                                                  |
+------------+-----------+---------------------+-------------------------------------------+-------------------------------------------------------+
| Int        | int, long | INT                 | TINYINT, SMALLINT, MEDIUMINT, INT, BIGINT | SERIAL, BIGSERIAL, SMALLSERIAL, INT, BIGINT, SMALLINT |
+------------+-----------+---------------------+-------------------------------------------+-------------------------------------------------------+
| Float      | float     | REAL, FLOAT, DOUBLE | FLOAT, REAL, DOUBLE PRECISSION            | FLOAT, REAL, DOUBLE PRECISSION                        |
+------------+-----------+---------------------+-------------------------------------------+-------------------------------------------------------+
| Decimal    | Decimal   | VARCHAR, TEXT       | DECIMAL, NUMERIC                          | DECIMAL, NUMERIC, MONEY                               |
+------------+-----------+---------------------+-------------------------------------------+-------------------------------------------------------+
| UUID       | uuid.UUID | TEXT                | BLOB                                      | UUID                                                  |
+------------+-----------+---------------------+-------------------------------------------+-------------------------------------------------------+
| Unicode    | unicode   | VARCHAR, TEXT       | VARCHAR, CHAR, TEXT                       | VARCHAR, CHAR, TEXT                                   |
+------------+-----------+---------------------+-------------------------------------------+-------------------------------------------------------+
| RawStr     | str       | BLOB                | BLOB, BINARY, VARBINARY                   | BYTEA                                                 |
+------------+-----------+---------------------+-------------------------------------------+-------------------------------------------------------+
| Pickle     | any       | BLOB                | BLOB, BINARY, VARBINARY                   | BYTEA                                                 |
+------------+-----------+---------------------+-------------------------------------------+-------------------------------------------------------+
| Json       | dict      | BLOB                | BLOB                                      | JSON                                                  |
+------------+-----------+---------------------+-------------------------------------------+-------------------------------------------------------+
| DateTime   | datetime  | VARCHAR, TEXT       | DATETIME, TIMESTAMP                       | TIMESTAMP                                             |
+------------+-----------+---------------------+-------------------------------------------+-------------------------------------------------------+
| Date       | date      | VARCHAR, TEXT       | DATE                                      | DATE                                                  |
+------------+-----------+---------------------+-------------------------------------------+-------------------------------------------------------+
| Time       | time      | VARCHAR, TEXT       | TIME                                      | TIME                                                  |
+------------+-----------+---------------------+-------------------------------------------+-------------------------------------------------------+
| TimeDelta  | timedelta | VARCHAR, TEXT       | TEXT                                      | INTERVAL                                              |
+------------+-----------+---------------------+-------------------------------------------+-------------------------------------------------------+
| List       | list      | VARCHAR, TEXT       | TEXT                                      | ARRAY[]                                               |
+------------+-----------+---------------------+-------------------------------------------+-------------------------------------------------------+
| Enum       | str       | INT                 | INT                                       | INT                                                   |
+------------+-----------+---------------------+-------------------------------------------+-------------------------------------------------------+
| NativeEnum | str, int  | INTEGER             | ENUM                                      | ENUM                                                  |
+------------+-----------+---------------------+-------------------------------------------+-------------------------------------------------------+

All those properties except **NativeEnum** are common |storm| properties. The **NativeEnum** property class is just a convenience class that we created to support legacy already designed databases that uses native Enum types and the scenario where we can't change this because the databse is used by other applications that we can't modify to switch to Int type.

.. warning::

    The use of the native enum type in MySQL is considered by a considerable proportion of developers as a bad practice and something really evil http://kcy.me/nit3

    In the postgres world there are a lot of libraries and frameworks that doesn't supports the native PostgreSQL enum type, we do, but be careful

