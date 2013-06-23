.. _installation_guide:

Mamba installation guide
========================

Mamba is written in the Python programming language and supports only version 2.7 of the language (some mamba components doesn't support Python 3.x yet). Mamba also need a database server `SQLite <http://sqlite.org/>`_, `MySQL <http://mysql.com/>`_, `MariaDB <https://mariadb.org/>`_ or `PostgreSQL <http://www.postgresql.org/>`_ in order to create and use schemes through `Storm ORM <http://storm.canonical.com>`_. For HTML rendering, mamba uses the `Jinja2 <http://jinja.pocoo.org/docs/>`_ templating system.

In order to execute mamba tests suite `doublex <https://bitbucket.org/DavidVilla/python-doublex>`_ and `PyHamcrest <http://pythonhosted.org/PyHamcrest/>`_ are required.

To build the documentation, Fabric must be installed on the system.

Installation Step
-----------------

1. :ref:`Dependencies`
    1. :ref:`Mandatory Dependencies`
    2. :ref:`Optional Dependencies`
2. :ref:`Installing Mamba`
    1. :ref:`The easy way`
    2. :ref:`Living on the edge`
3. :ref:`Using Mamba`

.. _Dependencies:

Dependencies
------------

Those are the mamba framework dependencies

.. _Mandatory Dependencies:

Mandatory Dependencies
......................

The following dependencies must to ve satisfied to install mamba.

* `Python <http://python.org>`_, version >= 2.7 <= 2.7.5 (3.x is not supported)
* `Twisted <http://www.twistedmatrix.com>`_, version >= 10.2.0
* `Storm <http://storm.canonical.com>`_, version >= 0.19
* `zope.component <http://docs.zope.org/zope.component/>`_
* `transaction <http://www.zodb.org/zodbbook/transactions.html>`_
* `Jinja2 <http://jinja.pocoo.org/docs/>`_, version >= 2.4

Is pretty possible that you also need a database manager and teh corresponding Python bindings for it. The database can be either SQLite, MySQL, MariaDB (recommended) or PostgreSQL (recommended).

For SQLite database
~~~~~~~~~~~~~~~~~~~

As you must be using Python 2.7 SQLite should be already built on it. This maybe is not true if you compiled Python interpreter yourself, in that case make sure you compile it with ` --enable-loadable-sqlite-extensions`` option.

If you are using PyPy, SQLite should be always compiled and present in your installation.

For MySQL and MariaDB databases
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The `MySQLdb <http://sf.net/projects/mysql-python>`_ driver should do the work for both database managers.

For PostgreSQL databse
~~~~~~~~~~~~~~~~~~~~~~

The `psycopg2 <http://pypi.python.org/pypi/psycopg2>`_ driver is our target for PostgreSQL databases if we are using the CPython interpreter

If you are using PyPy as your interpreter you need to install `psycopg2ct <https://github.com/mvantellingen/psycopg2-ctypes>`_ instead. Psycopg2ct is a psycopg2 implementation that uses ctypes and is just the boy that we want to do the job in PyPy.

.. warning::

    Versions of psycopg2 (CPython) higher than 2.4.6 doesn't work with Storm so you have to be sure to install a version lower than 2.5 that is the current version as May 2013


.. _Optional Dependencies:

Optional Dependencies
.....................

The following dependencies must be satisfied if we are planning on running mamba tests, building the documentation ourselves or contributing with the mamba project

* `doublex <https://bitbucket.org/DavidVilla/python-doublex>`_, version >= 1.5.1
* `PyHamcrest <http://pythonhosted.org/PyHamcrest/>`_
* `sphinx <http://sphinx-doc.org>`_, version >= 1.1.3
* `fabric <http://fabfile.org>`_
* `virtualenv <https://pypi.python.org/pypi/virtualenv/1.9.1>`_
* `pyflakes <https://launchpad.net/pyflakes>`_
* `pep8 <http://github.com/jcrocholl/pep8>`_

.. _Installing Mamba:

Installing Mamba
----------------

There are three ways to install mamba in your system.

The first one is install all the mamba dependencies as with any other software, downloading it from sources, precompiled binaries or just using your distribution package manager.

The second one is using ``pip`` or ``easy_install`` as::

    $ sudo pip install mamba-framework

.. _The easy way:

The easy way: PyPI - the Python Package Index
.............................................

The third one is using virtualenv to create a virtual environment for your mamba framework installation and then using ``pip`` on it, this is the recommended way as well::

    $ virtualenv --no-site-packages -p /usr/bin/python --prompt='(mamba-python2.7) ' mamba-python2.7
    $ source mamba-python2.7/bin/activate
    $ pip install mamba-framework
    $ pip install MySQL-Python

Or if you prefer to use ``virtualenvwrapper``::

    $ mkvirtualenv --no-site-packages -p /usr/bin/python --prompt='(mamba-python2.7) ' mamba-python2.7
    $ pip install mamba-framework
    $ pip install MySQL-Python

We recommend the use of ``virtualenvwrapper`` in development environments to be cleaner and easier to maintain.

.. _Living on the edge:

Living on the edge
..................

If you like to live in the edge you can clone the mamba's `GitHub repository <https://github.com/DamnWidget/mamba>`_ and use the ``setup.py`` script to install it yourself::

    $ git clone https://github.com/DamnWidget/mamba
    $ cd mamba
    $ mkvirtualenv --no-site-packages -p /usr/bin/pypy --prompt='(mamba-dev-pypy) ' mamba-dev-pypy
    $ pip install -r requirements.txt
    $ ./tests
    $ python setup.py install

.. warning::

    The mamba GitHub repository is under heavy development, we dont guarantee the stability of the mamba in-development version

.. _Using Mamba:

Using Mamba
-----------

Once you have mamba installed in yout system, you should be able to generate a new project using the ``mamba-admin`` command line tool.

**Enjoy it!**

|
