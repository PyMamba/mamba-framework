.. _MVC_and_hierarchy:

=========================
Mamba and the MVC pattern
=========================

According to Wikipedia; *Model View Controller (MVC) is a software architecture, currently considered as an architectural pattern used in software engineering. The pattern isolates "domain logic" (the application logic for the user) from input and presentation (GUI), permitting independent development, testing and maintenance of each.*

Mamba implements the MVC pattern using Jinja2 templates as the :ref:`view`, the :ref:`model` and the :ref:`controller` components. In mamba, the routing system is integrated into the controller itself.

Is mamba meant to be a real MVC implementation?
-----------------------------------------------

That depends on the interpretation of the paragraph above. Mamba applications are implemented using a MVC like pattern as we separate our business logic from the view (that onlyy knows how to render HTML), the controllers receive inputs as HTTP requests and initiates responses by calling methods in model objects that interacts with different data sources, interpret that data and send results back to the view (or send it through JSON or sockets to third parties).

The last description can be defined as a MVC pattern implementation or not depending from the point of view. Anyway, that's not important, the point is understand that mamba isolates the logic from the data from the presentation of the data is all that you are going to want to take care of.

=================================
Standard mamba application layout
=================================

A mamba standard application layout is as follows::

    application
     └                      →
    config                  →
     └
    docs                    →
     └
    static                  →
     └
    twisted                 →
     └
    LICENSE                 →
    README.rst              →
    app_name.py             →
    mamba_services.py       →
