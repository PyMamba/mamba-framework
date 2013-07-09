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
========================
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

    The use of the native enum type in MySQL is considered by some developers as a bad practice and something really evil http://kcy.me/nit3

Properties in deeper detail
===========================
A property is a |storm| object that *maps* our classes properties with a related field in the database and perform several other operations as cache values among others. we have as many property types as we shown already in the table above.

All property classes defined a class level property called ``variable_class`` that is an object that represents the value stored in the database as Python and is the part of the library that effectively *map* the Python representation of the value with the value itself as is stored in the database.

Variables are responsible for set and get values on and from the underlying database backend and perform any special operation that is needed to convert the native database types into Python ones.

Property constructor parameters
-------------------------------

The parameters that are accpeted depends in two factors:

    1. The type of the property
    2. The selected underlying database backend

All the options that we can pass to the constructor are optional and some of them has no effects at all in some database backends. Mamba defines the following common parameters:

    * **name**: The column name in the database. If you set this parameter, the database field and the class attribute can differ. So for example you can have a class attribute called ``customer_id`` while in the database the field is called ``id``
    * **primary**: if you set this parameter as ``True``, this attribute is being considered to map the primary key of the database table. You can create compound keys using the class level definition ``__storm_primary__`` attribute instead.
    * **default**: The default value for the property
    * **default_factory**: A factory which returns default values for the property. Mainly used when the default value is a mutable one.
    * **validator**: A callable object that takes three arguments. The validator has to return the value that the property should be set to, if the validator raises an exception, then the property is not set at all. You can't use validators on references or reference sets but is can be used on a foreign id property to achieve the same result as having a validator on the reference itself. Don't worry if you don't understand this right now, it should be clear in next steps. The three arguments taken are:
        a. the object that the property is attached to
        b. the attribute name as a string
        c. the value that is being set
    * **size** (*special behaviour*): The behaviour of this attribute differs depending on the database backend and the type of the property we are settings but mainly is sets the size of the field we are defining in the database.
    * **unsigned** (*special behaviour*): The ``unsigned`` parameter has different behaviours depending in the database engine and the type as well. Basically, it sets a numeric field as unsigned, this is mainly used with *MySQL/MariaDB* database engines.
    * **auto_increment** (*special behaviour*): As his friends above, this parameters has special meanings depending on database engine and field type. It's used to set a column as auto increment (mainly primary keys id's).
    * **array** (*postgres only*): This parameter is used to define an array type for PostgreSQL databases. PostgreSQL allows table columnns to be defined as variable-length multidimensional arrays

The **size**, **unsigned**, **auto_increment** and **array** attributes are not present on Storm, they are implemented only in Mamba and it's utility is closely related to the ability of mamba to generate SQL schemas using Python classes definitions.

Defining compound keys
----------------------

To define a compound key we have to use the ``__storm_primary__`` class-level attribute and set it as a tuple with the names of the properties that composes the primary key:

.. sourcecode:: python

    from storm.locals import Int
    from mamba.application import model

    class Dummy(model.Model):

        __storm_table__ = 'dummy'
        __storm_primary__ = 'id', 'status'

        id = Int()
        status = Int()

Understanding size
------------------

If we set the ``size`` parameter as ``True`` in an :class:`~storm.locals.Unicode` property, mamba will use it to specify the length of the varchar in the SQL representation. For example:

.. sourcecode:: python

    name = Unicode(size=64)

will be mapped to

.. code-block:: sql

    name VARCHAR(64)

in the resulting SQL schema. It works with any type of database backend that we set.

If the Property type that we use is :class:`~storm.locals.Decimal` it will work on MySQL/MariaDB **only** and should be completely ignored by PostgreSQL and SQLite backends. In the case of MySQL and :class:`~storm.locals.Decimal` the ``size`` attribute has special meaning depending on the type that you use to define it. That is in this way because you can define a size and a precission in the decimal part of the value:

.. sourcecode:: python

    some_field = Decimal(size=(10, 2))  # using a tuple
    some_field = Decimal(size=[10, 2])  # using a list
    some_field = Decimal(size=10.2)     # using a float
    some_field = Decimal(size='10,2')   # using a string
    some_field = Decimal(size=10)       # using an int (precission is set to 2)

In the above examples, the size is set to 10 and the precission to 2, in the case of use an ``int`` type, the precission is infered to 2 by default.

If the Property type is :class:`~storm.locals.Int` mamba should ignore it for PostgreSQL and SQLite, if the configured backend is MySQL, mamba will use the given parameter as the size of the int:

.. sourcecode:: python

    age = Int(size=2)

should be mapped to

.. code-block:: sql

    age INT(2)

Some notes about unsigned
-------------------------

Unsigned is completely ignored by PostgreSQL and SQLite backends so it has no effect at all if you are using any of them.

The auto_increment attribute
----------------------------

This attribute sets a colums or field as ``AUTO INCREMENT`` in MySQL and MariaDB backends if it's present and ``True`` in a :class:`~storm.locals.Int` property, otherwise is ignored. This is normally used with ``primary`` attribute also set as ``True``.

If you define ``auto_increment`` as ``True`` in a :class:`~storm.locals.Int` type property using a PostgreSQL backend, then it will be automaticaly transformed to a ``serial`` type.

This attribute is ignored when using SQLite backend.

Model operations
================

Create and insert a new object into the database is pretty straightforward, we just have to create a new instance of our model and cal the ``create`` method on it:

.. sourcecode:: python

    >>> dummy = Dummy()
    >>> dummy.name = u'The Dummy'
    >>> dummy.create()

Read a model instance (or row) from the database is as easy as using the ``read`` method of the :class:`~mamba.application.model.Model` class with the id of the row we want to get from the database:

.. sourcecode:: python

    >>> dummy = Dummy().read(1)

Update is performed in the same easy way, we just modify our object and call the ``update`` method on it:

..sourcecode:: python

    >>> dummy.name = u'Modified Dummy'
    >>> dummy.update()

Finally the delete operation is not different, we just call the ``delete`` method from our object (note that this doesn't delete the object reference itself, only the databse row):

.. sourcecode:: python

    >>> dummy.delete()

.. note::

    In mamba **CRUD** operations are executed as |twisted| transactions in the model object if we don't override the methods to have a different behaviour.



References
==========

Of course we can define references between models (and between tables by extension) intanciating :class:`~storm.locals.Reference` and :class:`~storm.locals.ReferenceSet` objects in our model definition:

.. sourcecode:: python

    from storm.locals import Int, Reference
    from mamba.application import model

    from application.model.dojo import Dojo

    class Figther(model.Model):

        __storm_table__ = 'figther'

        id = Int(primary=True, auto_increment=True, unsigned=True)
        dojo_id = Int(unsigned)
        dojo = Reference(dojo_id, Dojo.id)

In the previous example we defined a ``Figther`` class that define a many-to-one reference with the ``Dojo`` class imported from the dojo model. As this reference has been set we can use the following code to refer to the figther's dojo in our application:

.. sourcecode:: python

    >>> figther = Figther().read(1)
    >>> print(figther.dojo.id)
    1
    >>> print(figther.dojo.name)
    u'SuperDojo'

