.. _access_sql_database:

===================
Using SQL databases
===================

Mamba provides access to SQL databases through the :class:`~mamba.core.model.Model` class in asyncrhonous or synchronous way using the same database connection. Actually, Mamba supports **SQLite**, **MySQL/MariaDB** and **PostgreSQL** databases. In order to connect to a database, you have to configure the connection details in your application ``config/database.json`` file:

.. code-block:: json

    {
        "max_threads": 20,
        "min_threads": 5,
        "auto_adjust_pool_size": true,
        "drop_table_behaviours": {
            "drop_if_exists": false,
            "restrict": true,
            "cascade": true
        },
        "uri": "backend://user:password@host/dbname",
        "create_table_behaviours": {
            "create_table_if_not_exists": false,
            "drop_table": false
        }
    }

Ths database configuration file can be created manually or using the ``mamba-admin`` command line tool using a valid URI or passing explicit parameters::

    $ mamba-admin sql configure --uri=backend://user:password@host/dbname

Or::

    $ mamba-admin sql configure --username='user' --password='password' --hostname='hostname' --backend='backend' --database='dbname'

The above two commands are exactly the same, both of them generates a new database config file with default options and connects to the given backend (can be one of: sqlite, mysql or postgres) with the given user and password credentials in the given host and the given database.

The following is a list of all the options that can be passed to the ``mamba-admin sql configure`` command::

    Usage: mamba-admin [options] sql [options] command configure [options]
    Options:
      -p, --autoadjust-pool       Auto adjust the database thread pool size?
      -c, --create-if-not-exists  If present, when mamba try to create a new table
                                  adds an `IF EXISTS` clause to the SQL query
      -d, --drop-table            If present, mamba will drop any table (if exists)
                                  before to create it. Note this option is not
                                  compatible with `create-if-not-exists
      -e, --drop-if-exists        If present, mamba will add an `IF EXISTS` clause
                                  to any intent to DROP a table
      -r, --non-restrict          If present, mamba will NOT use restrict drop
      -a, --cascade               If present, mamba will use CASCADE in drops
      -n, --noquestions           When this option is set, mamba will NOT ask
                                  anything to the user that means it will delete any
                                  previous database configuration and will accept
                                  any options that are passed to it (even default
                                  ones).Use with caution
          --uri=                  The database connection URI as is used in Storm.
                                  Those are acceptable examples of format:

                                  backend:database_name
                                  backend://hostname/database_name
                                  backend://hostname:port/database_name
                                  backend://username:password@hostname/database_name
                                  backend://hostname/database_name?option=value
                                  backend://username@/database_name

                                  Where backend can be one of sqlite, mysql or
                                  postgres. For example:

                                  sqlite:app_db slite:/tmp/tmp_database
                                  sqlite:db/my_app_db
                                  mysql://user:password@hostname/database_name
                                  postgres://user:password@hostname/database_name

                                  Note that you can also use --hostname --user and
                                  --password options instead of the URI syntax
                                  [default: sqlite]

          --min-threads=          Minimum number of threads to use by the thread
                                  pool [default: 5]
          --max-threads=          Maximum number of thread to use by the thread pool
                                  [default: 20]
          --hostname=             Hostname (this is optional)
          --port=                 Port (this is optional)
          --username=             Username which connect to (this is optional)
          --password=             Password to connect (this is optional)
          --backend=              SQL backend to use. Should be one of
                                  [sqlite|mysql|postgres] (this is optional but
                                  should be present if no URI is being to be used)
                                  [default: sqlite]
          --database=             database (this is optional but should be suply if
                                  not using URI type configuration)
          --path=                 database path (only for sqlite)
          --option=               SQLite additional option
          --version               Show version information and exit
          --help                  Display this help and exit.

The database URI
================

Mamba uses a valid `URI <http://en.wikipedia.org/wiki/Uniform_resource_identifier>`_ as parameters to connect with the database.

SQLite URIs
-----------

The simplest valid URI that we can use for our mamba application is just the SQLite in memory database:

.. sourcecode:: python

    "uri": "sqlite:"

Relative (to the web application root directory) or absolute paths can be used for database name/location, the following are all valid possible sqlite configurations:

.. sourcecode:: python

    "uri": "sqlite:foo"
    "uri": "sqlite:/home/user/foo"
    "uri": "sqlite:///foo"
    "uri": "sqlite:///home/user/foo"

If the database doesn't exists yet, mamba will create it when we try to use first. If the path doesn't exists or is not accessible (e.g. permission denied), an exception ``OperationalError`` will be raised.

SQLite accepts one option in the option part of the URI. We can set the time that SQLite will wait when trying to obtain a lock on the database. The default value for the timeout is five seconds, an example of the above is as follows:

.. sourcecode:: python

    "uri": "sqlite:dummy?timeout=0.5"

This will create a new SQLite database connection with a timeout of half a second.

MySQL/MariaDB URIs
------------------

MySQL and MariaDB share syntax for URI's:

.. sourcecode:: python

    "uri": "mysql://username:password@hostname:port/database_name"

.. note::

    MySQL supports depends on the `MySQLdb <http://mysql-python.sourceforge.net/>`_ |python| module


PostgreSQL
----------

Syntax for PostgreSQL is exactly the same than MySQL/MariaDB but replacing the ``mysql://`` for the right ``postgres://`` scheme:

.. sourcecode:: python

    "uri": "postgres://username:password@hostname:port/database_name"

.. note::

    PostgreSQL supports depends on the `psycopg2 <http://initd.org/psycopg/>`_ Python module

.. warning::

    If you are planning to use PyPy as your interpreter, you **must** install `psycopg2ct <https://github.com/mvantellingen/psycopg2-ctypes>`_ that is an implementation of the psycopg2 module using ctypes

Create or dump SQL schema from mamba models
===========================================

In mamba we don't create a schema config file that is then used to generate our model classes, instead of that, we define our model classes and then we generate our SQL schema using our already defined Python code.

To create our database structure in live or dump a SQL file with the schema (for whatever SQL backend we configured) we use the ``mamba-admin sql create`` subcommand in the command line interface, so for example to dump the schema into a file we should use::

    $ mamba-admin sql create schema.sql

To dump it to the stdout::

    $ mamba-admin sql create -d

And for create it in live in the database (this may delete all your previous data, be careful)::

    $ mamba-admin sql create -l

.. note::

    If you don't want Mamba to generate SQL for a specific(s) table(s), you can set the class-level attribute ``__mamba_schema__`` to ``False``.
    This will also prevent Mamba of dropping this table or truncating its data when you use the ``reset`` command.


Dump SQL data from the database
===============================

If you ever used ``mysqldump`` you will be familiarized with ``mamba-admin sql dump`` command. It dumps the actual data into the database to the stdout. Doesn't matter which database backend you are using, it works with SQLite, MySQL and PostgreSQL and you don't need to have installed ``mysqldump`` command to dump MySQL databases::

    $ mamba-admin sql dump > database-dump.sql

The above command will dump the database into a file in the current directory named ``database-dump.sql``

Truncating all data in your database
====================================

Some times we need to truncate all tables in our database, normally because development tasks. For that scenario you can use the ``reset`` command as::

    $ mamba-admin sql reset --noquestions

The above command will reset all your data without any question, please, be careful with this command.

Future plans
============

For next releases, a live database migration tool is intended to be added to the framework so the developer can just switch from a RDBMS to another one without losing his data.

=========================================
The Mamba |storm| - |twisted| integration
=========================================

Mamba uses the |storm|'s |twisted| ``@transact`` integration added in |storm| v0.19. It also creates a ``ThreadPool`` service on initialization time so you don't have to take care of do it yourself. The *transact* system is quite simple:

    Any model method that is decorated with the ``@transact`` decorator is executed in a separate thread into the mamba database thread pool and returns a |twisted| `deferred <http://twistedmatrix.com/documents/current/core/howto/defer-intro.html>`_ object. Any method that is not decorated by ``@transact`` is just using regular storm features and it can't run asynchronous.

Using the *transact* system has advantages and disadvantages:
    * The main advantage is it runs asynchronous so it **doesn't block** the |twisted| reactor loop.
    * The main disadvantage is that any return value from the decorated (with ``@transact``) method must **not** contain any reference to Storm objects because they were retrieved in a different thread and of course can't be used outside it. This put limits in some awesome |storm| features that can be used within the decorated method only, ``Reference`` and ``ReferenceSets`` for example.

The transact mechanism can be dangerous in environments where serialization or sinchronization of the data is a requirement because using the ``@transact`` decorated methods can end in unexpected race conditions.

The developer should think about what she needs and use ``@transact`` or not following what the application or the feature or system that is being implemented needs to fit.

Howto use Storm in mamba models?
================================

Mamba's enterprise system take care of any initialization that is needed by the underlying |storm| library, we don't have to care about create database connections or stores. We can use it with CPython or PyPy without any type of code modification.

The Store object
----------------

|storm| (and mamba by extension) uses *stores* to operate with the underlying database. You can take a look to the `Storm API documentation <http://people.canonical.com/~therve/storm/storm.store.Store.html>`_ to retrieve a complete list of Store methods and properties.

The mamba's enterprise system initialize a valid |storm| Store object for us always that we need it using the ``database`` model property ``store()`` method:

.. sourcecode:: python

    store = self.database.store()

Every model object has a copy of the ``database`` object that can be used to retrieve stores and other database related information.

Stores are used to retrieve objects from the database, to insert and update objects on it and of course to execute SQL queries directly to the database. Store is like a traditional ``cursor`` but much more flexible.

If we need to create and insert a new row into the database we just instantiate the model object and then add it to a valid store:

.. sourcecode:: python

    peter = User()
    peter.name = u'Peter Griffin'

    store = self.database.store()
    store.add(peter)

Once an object is added to or retrieved from a store, we can verify if it is bound or related to an store easily:

.. sourcecode:: python

    >>> Store.of(peter) is store
    True
    >>> Store.of(User()) is store
    False

If we are using the ``@transact`` decorator in our methods we don't have to care about commit to the database because that is performed in an automatic way by the ``@transact`` decorator, otherwise we **must** call the ``commit`` method of the store object:

.. sourcecode:: python

    store.commit()

If we made a mistake we can just call the ``rollback`` method in the same way.

Of course we can use the store object to find rows already inserted on the database. The following is an example of how to use a store to find an user in the underlying database:

.. sourcecode:: python

    store = self.database.store()
    user = store.find(User, User.name == u'Peter Griffin').one()

We can also retrieve the object using its primary key:

.. sourcecode:: python

    pk_user = store.get(Person, 1)

Stores caches objects as default behaviour so we can check that ``user`` and ``pk_user`` are efectively the same object:

.. sourcecode:: python

    >>> pk_user is user
    True

Each store has an object cache, when an object is linked to a store, it is cached by the store for as long there is a reference to the object somewhere, or while the object becomes dirty (has changes on it). In this way |storm| make sure that we don't access to the database when is not necessary to retrieve the same objects.

Modifiying objects with the Store
---------------------------------

We dont have to retrieve an object from the database and then modify and save it, we can just use the Store to do the work for us using expressions:

.. sourcecode:: python

    store.find(User, User.name == u'Peter Griffin').set(name='Peter Sellers')

How do I use stores in an asynchronous way?
===========================================

Just decorate your model methods with the ``@transact`` decorator and make sure to don't return any |storm| object from that method:

.. sourcecode:: python

    from mamba.application import model
    from storm.locals import Int, Unicode
    from storm.twisted.transact import transact

    class Dummy(model.Model):

        __storm_table__ = 'dummy'

        id = Int(primary=True)
        name = Unicode()

        def __init__(self, name):
            self.name = unicode(name)

        @transact
        def get_last(self):
            """
            Get the last inserted row from the database.
            This is not thread safe
            """
            store = self.database.store()
            return store.find(Dummy).order_by(Dummy.id).last()

The ``get_last`` method above will retrieve the last inserted row in the database, as we are using the ``@transact`` decorator we couldn't use ``Reference`` or ``ReferenceSet`` in the returned object cos those are lazy evaluated and the object was created in a different thread, if we ever try to do that we will get an exception from |storm| ZStore module.

If we don't want to use an asynchronous operation we can just remove the ``@transact`` line and it will work perfectly synchronous, of course the limitations about using references with the returned object does not apply on this scenario.

How do I use a store from outside the model method?
===================================================

Even mamba allows us to use Store objects everywhere, them are not supossed to be used outside the model but nothing stop you tu use it in the controller or whatever other part of your application.

If you think that you need to use a store object from outside your model class then you can do it in several ways:

1. Don't decorate a method in your moddel with ``@transact`` and then return the store from it. As this store as been created in the same thread that the rest of the application you can use it anywhere.
2. Just retrieve a store object executing the ``database.store()`` object directly from your model at class level:
    .. sourcecode:: python

        from application.model.dummy import Dummy

        store = Dummy.database.store()
        dummy = store.get(Dummy, 1)

.. warning::

    Please, be careful, we recommend energically to don't use stores outside the model. It doesn't follow the MVC pattern and violates the encapsulation principle.

Should I share stores between threads?
--------------------------------------

Please no, everytime that you call the ``database.store()`` method in the model object, mamba gives you a ready to use Store for the thread that you are calling the method from. Don't even try to share stores between threads. That means that you are not able to share stores between methods if they are decorated with the ``@transact`` decorator.

|
