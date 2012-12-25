.. _api:

API
===

.. module:: mamba
    :synopsis: public Mamba API

This is the Mamba API documentation.


Mamba Application
-----------------

Objects for build Mamba Applications

.. autoclass:: Mamba
    :members:

.. autoclass:: ApplicationError


AppStyles
.........

.. autoclass:: AppStyles
    :members:
    :inherited-members:


Controllers
...........

.. autoclass:: Controller
    :members:

.. autoclass:: ControllerManager
    :members:
    :inherited-members:


Models
......

.. autoclass:: Model
    :members:


Mamba Core
----------

Core components of the Mamba framework itself.

Interfaces
..........

Interfaces that are part of the Mamba Core, you are supossed to never use those ones unless you are developing new features for the Mamba framework itself.

.. autoclass:: mamba.core.interfaces.INotifier
    :members:

    .. method:: _notify(ignore, file_path, mask)

        :param ignore: ignored parameter
        :param file_path: :class:`twisted.python.filepath.Filepath` on which the event happened
        :param mask: inotify event as hexadecimal mask
        :type mask: int

    .. attribute:: notifier

        A :class:`twisted.internet.inotify.INotify` instance where to watch a FilePath


.. autoclass:: mamba.core.interfaces.IController
    :members:

    :param name: Controller's name
    :type name: str
    :param desc: Controller's description
    :type desc: str
    :param loaded: True if the controller has been loaded, otherwise
                   returns False
    :type loaded: bool

.. autoclass:: mamba.core.interfaces.IDeployer
    :members:

.. autoclass:: mamba.core.interfaces.IResponse
    :members:

    :param code: the HTTP response code
    :type code: int
    :param body: the HTTP response body
    :type body: string
    :param headers: the HTTP response headers
    :type headers: dict


Decorators
..........


.. currentmodule:: mamba.core.decorators

.. autofunction:: mamba.core.decorators.cache
.. autofunction:: mamba.core.decorators.unlimited_cache


Http
----

Mamba Http Headers

.. autoclass:: mamba.http.headers.Headers
    :members:

Utils
-----

Subpackage containing the modules that implement common utilities

Borg
....

.. autoclass:: mamba.utils.borg.Borg
    :members:


CamelCase
.........

.. autoclass:: mamba.utils.camelcase.CamelCase
    :members:


Converter
.........

.. autoclass:: mamba.utils.converter.Converter
    :members:



Web
---

Subpackage containing the modules that implement web stuff for projects

AsyncJSON
.........

.. autoclass:: mamba.web.asyncjson.AsyncJSON
    :members:


Page
....

.. autoclass:: mamba.web.Page
    :members:
    :inherited-members:

Response
........

.. autoclass:: mamba.web.Response
    :members:

.. autoclass:: mamba.web.Ok
    :members:

.. autoclass:: mamba.web.NotFound
    :members:

.. autoclass:: mamba.web.BadRequest
    :members:

.. autoclass:: mamba.web.Conflict
    :members:

.. autoclass:: mamba.web.AlreadyExists
    :members:

.. autoclass:: mamba.web.NotImplemented
    :members:

.. autoclass:: mamba.web.InternalServerError
    :members:


Routing
.......

.. autoclass:: mamba.web.Route
    :members:

.. autoclass:: mamba.web.Router
    :members:

.. autoclass:: mamba.web.RouteDispatcher
    :members:


Stylesheets
...........

.. autoclass:: mamba.web.Stylesheet
    :members:

.. autoclass:: mamba.web.StylesheetError
    :members:

.. autoclass:: mamba.web.InvalidFile
    :members:

.. autoclass:: mamba.web.InvalidFileExtension
    :members:

.. autoclass:: mamba.web.FileDontExists
    :members:

Url Sanitizer
.............

.. autoclass:: mamba.web.url_sanitizer.UrlSanitizer
    :members:


Extension Point
---------------

.. autoclass:: mamba.ExtensionPoint
