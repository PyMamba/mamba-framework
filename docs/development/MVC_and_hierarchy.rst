.. _MVC_and_hierarchy:

=========================
Mamba and the MVC pattern
=========================

According to Wikipedia; *Model View Controller (MVC) is a software architecture, currently considered as an architectural pattern used in software engineering. The pattern isolates "domain logic" (the application logic for the user) from input and presentation (GUI), permitting independent development, testing and maintenance of each.*

Mamba implements the MVC pattern using Jinja2 templates as the **view**, then Mamba components act as the **model** and the **controller**. In Mamba, the routing system is integrated into the controller itself.

Is Mamba meant to be a real MVC implementation?
-----------------------------------------------

That depends on the interpretation of the paragraph above. Mamba applications are implemented using a MVC like pattern as we separate our business logic from the view (that only knows about render HTML), the controllers receive inputs as HTTP requests and initiates responses by calling methods in model objects that interacts with different data sources, interpret that data and send results back to the view through the controller (or send it through JSON or sockets to third parties).

The last description can be defined as a MVC pattern implementation or not depending on the point of view. Anyway, Mamba isolates the logic of the data from the presentation of the data, that's all that you are going to want to take care of.

=================================
Standard Mamba application layout
=================================

A Mamba standard application layout is as follows::

    application                     → Application package
     └ controller                   → Application controllers
     └ model                        → Application models
     └ view                         → Application templates and scripts
        └ stylesheets               → CSS/LESS files
        └ scripts                   → JavaScript/Dart files
        └ templates                 → Jinja2 Templates
     └ lib                          → General library dependencies that are not part of the MVC and 3rd party libraries
    config                          → Configuration files
     └ application.json             → Application main configuration file
     └ database.json                → Application database configuration file (if applicable)
     └ installed_packages.json      → Application installed shared packagees (if applicable)
    docs                            → Application documentation directory
    static                          → Application assets durectory
    test                            → Application tests directory
    twisted                         → Twistd plugin for twisted daemonizer
    logs                            → Application logs directory
    LICENSE                         → LICENSE file
    README.rst                      → README file
    app_name.py                     → Application initialization file
    mamba_services.py               → File used internally by mamba to perform several tasks on application directory


The application directory
-------------------------

The ``application`` directory contains all our application Python code (with the exception of the shared packages and the ``ApplicationFactory``)

The ``application`` directory contains three directories to implement the MVC pattern and a fourth one where to place all the code that doesn't fit the MVC pattern and 3rd party libraries as well, all of them are Python packages:

    * application/controller        → Python package
    * application/model             → Python package
    * application/view              → Python package
    * application/lib               → Python package

The ``application`` directory is a package itself, meaning it contains an ``__init__.py`` file so you can add whatever other directory/package/module that you need. The application directory and all its contents are exported by default when you :ref:`pack <packing-an-application>` or install your application.

The config directory
--------------------

The ``config`` contains the application configuration files. Those files **must** be valid **JSON** formatted files. There are two main configuration files on mamba:

    * ``application.json``, this is the main configuration file for the application, if you need to add some configurable parameter to your application, this is the file to place it
    * ``database.json``, this file is used to configure database connections and it parameters

A third file is used to tell Mamba that we want to include some Mamba shared package in our application:

    * ``installed_packages.json``, this file contains a list of installed Mamba shared :ref:`packages <reusability>` that we want to use in our application

If you need to add some custom configuration file, you shoud place it inside this directory to follow convention.

The docs directory
------------------

The ``docs`` directory is used to store the application documentation. We use |sphinx|_ as documentation system but you can use whatever you want.

The static directory
--------------------

The ``static`` directory is used to store mainly images and other static data. You can use it to store and access CSS, JavaScript or HTML static files but is better if you do that using the templating system.

.. warning::

    All the files that you place in the static directory is publicly accessible from internet

The test directory
------------------

The ``test`` directory contains your application unit tests and integration tests


The twisted directory
---------------------

Twisted directory is used internally by mamba and |twisted| to daemonize your mamba applications, you don't have to care about this dIrectory and itS contents.

The logs directory
------------------

Mamba writes the log files in the ``logs`` directory if you don't configure other behaviour by yourself.

|