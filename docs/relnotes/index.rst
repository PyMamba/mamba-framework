Release Notes for Mamba v${version}
===================================

..
    Any new feature or bugfix should be listed in this file, for trivial fixes
    or features a bulleted list item is enough but for more sophisticated
    additions a subsection for their own is required.

Those are the release notes for Mamba v${version} released on ${release_date}.

Features
--------

This is the first Mamba release.

Routing System
~~~~~~~~~~~~~~

Mamba implements a custom routing system that don't uses the traditional
Twisted routing based on childs.

For more information refer to the routing system documentation

Database ORM Layer
~~~~~~~~~~~~~~~~~~

Mamba implements an ORM Database access layer in top of Storm and it's fully
integrated with Twisted Deferred system.

The supported database backends are:

* Postgres
* MySQL/MariaDB
* SQLite

Mamba adds several features to Storm making possible for example generate
database schemes using programatic configuration Python code.

For more information refer to the Mamba Storm integration documentation

Jinja2 Templating System
~~~~~~~~~~~~~~~~~~~~~~~~

Mamba integrates the Jinja2 Templating System in the routing and rendering
process but you are allowed to use whatever other templating system you want
(including Twisted Templating System of course).

For detailed information about Mamba Jinja2 templating integration refer to its
documentation.

Mamba Administration Command Line Interface Tools
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Mamba include a complete CLI toolset to manage and configure Mamba web
applications, you can use the `mamba-admin` script in your terminal to access
the complete toolset.

To get more information about `mamba-admin` refer to it's documentation.


Bug Fixes
---------

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

    git log ${current_version} ${version}
