Release Notes for Mamba ${version}
==================================

..
   Any new feature or bugfix should be listed in this file, for trivial fixes
    or features a bulleted list item is enough but for more sphisticated
    additions a subsection for their own is required.

Those are the release notes for Mamba ${version} released on ${release_date}.

Features
--------

* Added Unauthorized (401 HTTP) Response to predefined responses
* Added decimal size and precission using size property for MySQL decimal fields definitions::

    some_field = Decimal(size=(10, 2))  # using a tuple
    some_field = Decimal(size=[10, 2])  # using a list
    some_field = Decimal(size=10.2)     # using a float
    some_field = Decimal(size='10,2')   # using a string
    some_field = Decimal(size=10)       # using an int (precission is set to 2)

Bug Fixes
---------

* We were not using properly ZStorm/transaction and Twisted Transactor integration in Storm, now is fixed and a new `copy` helper method has been added to :class:`mamba.application.model.Model` class to allow simple object copy on user code because we can't use a store that has been created in a thread into the :class:`twisted.python.threadpool.ThreadPool` using the `@transact` decorator. If you need to pass initialized Storm objects directly to a view for whatever reasson you shouldn't use the `@transact` decorator at all (so you shouldn't use asynchronous call to the database for that).
* Now unhandled errors in Deferreds on routing module are displayed nicely in the logs file
* Model read method now returns a copy of the Sorm object that can be used in other threads if the optional parameter copy is True (it's False by default)
* Fixed a bug in create SQL mamba-admin command when used with live (-l) option
* Fixed a bug related with PyPy and it's lack of **set_debug** method in **gc** object

Deprecations
------------

Removals
--------

* Removed unused cleanups in controller tests
* Removed default update method in :class:`mamba.application.model.Model` object, the user code **must** implicit implement it

Uncompatible Changes
--------------------

Details
-------

If you need a more detailed description of the changes made in this release you
can use git itself using::

   git log ${current_version}..${version}
