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

Scripts
.......

.. autoclass:: mamba.application.scripts.Scripts
    :members:
    :inherited-members:

Controllers
...........

.. autoclass:: mamba.application.controller.ControllerError

.. autoclass:: Controller
    :members:

.. autoclass:: mamba.application.controller.ControllerProvider

.. autoclass:: ControllerManager
    :members:
    :inherited-members:


Models
......

.. autoclass:: mamba.application.model.MambaStorm

.. autoclass:: mamba.application.model.ModelError

.. autoclass:: Model
    :members:

.. autoclass:: mamba.application.model.ModelProvider

.. autoclass:: ModelManager
    :members:
    :inherited-members:


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
    :param loaded: true if the controller has been loaded, otherwise
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

.. autoclass:: mamba.core.interfaces.IMambaSQL
    :members:

    :param original: the original underlying SQL backend type

.. autoclass:: mamba.core.interfaces.ISession
    :members:

    :param session: A mamba session object


Decorators
..........


.. currentmodule:: mamba.core.decorators

.. autofunction:: mamba.core.decorators.cache
.. autofunction:: mamba.core.decorators.unlimited_cache


Core Services
.............

Core Services used by mamba applications

.. autoclass:: mamba.core.services.threadpool.ThreadPoolService
    :members:


Resource
........

Mamba Resource object extends Twisted web Resources mainly to integrate the Jinja2 templating system

.. autoclass:: mamba.core.resource.Resource
    :members:


Session
.......

.. autoclass:: mamba.core.session.MambaSession
    :members:

.. autoclass:: mamba.core.session.Session
    :members:


Templating
..........

Mamba integrates the Jinja2 templating system as a core component of the framework.

.. autoclass:: mamba.core.templating.MambaTemplate
    :members:

.. autoclass:: mamba.core.templating.Template
    :members:

.. autoclass:: mamba.core.templating.TemplateError

.. autoclass:: mamba.core.templating.NotConfigured


Deployment
----------

Mamba integrates the Fabric deployment library and it's used by Mamba itself to release new versions and deploy the framework to the live mamba web site. Too see an example of usage you can check the `mamba devel`_ package on GitHub.

.. mamba devel: https://github.com/DamnWidget/mamba_devel

.. autoclass:: mamba.deployment.deployer.DeployerImporter
    :members:

.. autofunction:: mamba.deployment.deployer.deployer_import

.. autoclass:: mamba.deployment.fabric_deployer.FabricDeployer
    :members:

.. autoclass:: mamba.deployment.fabric_deployer.FabricMissingConfigFile

.. autoclass:: mamba.deployment.fabric_deployer.FabricConfigFileDontExists

.. autoclass:: mamba.deployment.fabric_deployer.FabricNotValidConfigFile


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


config.Database
...............

This class is used to load configuration files in JSON format from the file system. If no config is provided a basic configuration based on SQLite is automatically created for us.

.. autoclass:: mamba.utils.config.Database
    :members:
    :inherited-members:

config.Application
..................

As with the previous one, this class is used to load configuration related with the application from files in JSON format in the file system. If no configuration file is provided, a basic configuration is automatically created for us.

.. autoclass:: mamba.utils.config.Application
    :members:
    :inherited-members:

Less
....

.. autoclass:: mamba.utils.less.LessCompiler
    :members:

.. autoclass:: mamba.utils.less.LessResource
    :members:
    :inherited-members:

Output
......

Output printing functionallity based and partially taken from Gentoo portage system

.. currentmodule:: mamba.utils.output



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

.. autoclass:: mamba.web.Found
    :members:

.. autoclass:: mamba.web.NotFound
    :members:

.. autoclass:: mamba.web.BadRequest
    :members:

.. autoclass:: mamba.web.Unauthorized
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


Scripts
.......

.. autoclass:: mamba.web.Script
    :members:

.. autoclass:: mamba.web.ScriptManager
    :members:

.. autoclass:: mamba.web.ScriptError
    :members:

.. autoclass:: mamba.web.script.InvalidFile
    :members:

.. autoclass:: mamba.web.script.InvalidFileExtension
    :members:

.. autoclass:: mamba.web.script.FileDontExists
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


WebSockets
..........

.. autoclass:: mamba.web.websocket.WebSocketProtocol
    :members:

.. autoclass:: mamba.web.websocket.WebSocketFactory
    :members:

.. autoclass:: mamba.web.websocket.HyBi07Frame
    :members:

.. autoclass:: mamba.web.websocket.HyBi00Frame
    :members:

.. autoclass:: mamba.web.websocket.InvalidProtocolVersionPreamble
    :members:

.. autoclass:: mamba.web.websocket.HandshakePreamble
    :members:

.. autoclass:: mamba.web.websocket.HyBi07HandshakePreamble
    :members:

.. autoclass:: mamba.web.websocket.HyBi00HandshakePreamble
    :members:

.. autoclass:: mamba.web.websocket.WebSocketError

.. autoclass:: mamba.web.websocket.NoWebSocketCodec

.. autoclass:: mamba.web.websocket.InvalidProtocolVersion

.. autoclass:: mamba.web.websocket.InvalidCharacterInHyBi00Frame

.. autoclass:: mamba.web.websocket.ReservedFlagsInFrame

.. autoclass:: mamba.web.websocket.UnknownFrameOpcode


Enterprise
----------

This is the package that give you access to Database layers. You can use traditional Open Source SQL solutions as `PostgreSQL <http://www.postgresql.org/>`_ PostgreSQL, `MySQL <http://www.mysql.com/>`_ or `SQLite <http://www.sqlite.org/>`_ as well as No-SQL Open Source solutions as `MongoDB <http://www.mongodb.org/>`_ (work in progress).

The SQL database access is performed through `Storm <http://storm.canonical.com>`_ with some monkey patching to make possible database creation from the Pthon defined model.

Mamba is supossed to work fine with Storm since revision 223 of the bazaar repository in Storm-0.12 but we only tested it with version 0.19.

SQL through Storm
.................

.. autoclass:: mamba.Database
    :members:

.. autoclass:: mamba.Model
    :members:

Specific SQL Backends and Adaptors (used internally by Mamba)
.............................................................

It's probable that you never use those ones by yourself


.. autoclass:: mamba.enterprise.sqlite.SQLite
    :members:
    :inherited-members:

.. autoclass:: mamba.enterprise.mysql.MySQL
    :members:
    :inherited-members:

.. autoclass:: mamba.enterprise.postgres.PostgreSQL
    :members:
    :inherited-members:

.. autoclass:: mamba.enterprise.database.AdapterFactory
    :members:


Monkey Patches
..............

.. autoclass:: mamba.enterprise.database.PropertyColumnMambaPatch
    :members:


Extension Point
---------------

.. autoclass:: mamba.ExtensionPoint
