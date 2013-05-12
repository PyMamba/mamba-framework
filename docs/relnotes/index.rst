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

Bug Fixes
---------

* We were not using properly ZStorm/transaction and Twisted Transactor integration in Storm, now is fixed and a new `copy` helper method has been added to :class:`mamba.application.model.Model` class to allow simple object copy on user code because we can't use a store that has been created in a thread into the :class:`twisted.python.threadpool.ThreadPool` using the `@transact` decorator. If you need to pass initialized Storm objects directly to a view for whatever reasson you shouldn't use the `@transact` decorator at all (so you shouldn't use asynchronous call to the database for that).

* Now unhandled errors in Deferreds on routing module are displayed nicely in the logs file

Deprecations
------------

Removals
--------

Uncompatible Changes
--------------------

Details
-------

If you need a more detailed description of the changes made in this release you
can use git itself using::

   git log ${current_version}..${version}
