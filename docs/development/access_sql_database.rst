.. _access_sql_database:

===================
Using SQL databases
===================

Mamba provides access to SQL databases through the :class:`~mamba.core.model.Model` class in asyncrhonous or synchronous way using the same database connection. Actually, Mamba supports **SQLite**, **MySQL/MariaDB** and **PostgreSQL** databases. In order to connect to a database, you have to configure the connection details in the ``config/database.json`` file:

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

Ths databse configuration file can be created by hand or using the ``mamba-admin`` command line tool::

    $ mamba-admin sql configure --autoadjust-pool --create-if-not-exists --noquestions --uri=backend://user:password@host/dbname

Or::

    $ mamba-admin sql configure --autoadjust-pool --create-if-not-exists --noquestions --username='user' --password='password' \
    --hostname='hostname' --backend='backend' --database='dbname'

The above two commands are exactly the same, both of them generates a new databse config file with ``auto_adjust_pool_size`` set as ``true``, ``create_table_if_not_exists`` behaviour for create tables and connects to the given backend (can be one of: sqlite, mysql or postgres) with the given user and password credentials in the given host and the given database.

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

Create or dump SQL schema from mamba models
===========================================

In mamba we don't create a schema config file that is used then to generate our model classes, instead of that, we define our model classes and then we generate our SQL schema using our already defined Python code.

To crate our database structure in live or dump a SQL file with the schema (for whatever SQL backend we configured) we use the ``mamba-admin sql create`` subcommand in the command line interface, so for example to dump the schema into a file we should use::

    $ mamba-admin sql create schema.sql

To dump it to the stdout::

    $ mamba-admin sql create -d

And for create it in live in the database (this may delete all your previous data, be careful)::

    $ mamba-admin sql create -l


Dump SQL data from the database
===============================

If you ever used ``mysqldump`` you will be familiarized with ``mamba-admin sql dump`` command. It dumps the actual data into the database to the stdout. Doesn't matter which databse backend you are using, it works with SQLite, MySQL and PostgreSQL and you don't need to have installed ``mysqldump`` command to dump MySQL databases::

    $ mamba-admin sql dump > database-dump.sql

The above command will dump the database into a file in the current directory named ``database-dump.sql``

Truncating all the data in your database
========================================

Some times we need to truncate all the tables in our database, normally because development tasks. For that scenario you can use the ``reset`` command as::

    $ mamba-admin sql reset --noquestions

The above command will reset all your data without any question, please, be careful with this command.

Future plans
============

For next releases, a live database migration tool is intended to be added to the framework so the developer can just switch from a RDBMS to another one without losing his data.

|
