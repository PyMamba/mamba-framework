.. _controller:

==========================
The Mamba controller guide
==========================

The controller is what connects your model and business logic with the views in the frontend part of the application. In Mamba we don't have routing system like Django does, in Mamba we use a request routing system similar to the one found in Bottle or Flask.

How it works?
=============

Every controller in a Mamba application inherits directly from the :class:`mamba.application.controller.Controller` class. A controller can define **action methods** and regular methods.

    * An action method is a method that is invoked by the underlying request routing system when our application receives a request. Each action in our controller has to fit in a route, we define routes using the ``route`` decorator and decorating the method to fit a route.
    * A regular method is just a normal method that is not decorated and is usually some kind of helper method that helps our controllers to make its work.

A controller can define as many action and regular emthods as is needed and every controller action represents a single URL segment of the application.

.. sourcecode:: python

    @route('/')
    def root(self, request. **kwargs):
        """Just an action method for the root of the controller
        """
        return Ok(sef.salutation())

    def salutation(self):
        """Just a regular method used as helper for our controller class
        """

        return 'Hello World!'

.. seealso::

    :doc:`routing`

Mamba create and handles an internal controller manager object that load all the controllers that are found in our application on initialization time and register all its routes with the routing system.

When a HTTP request is made from a client, it's captured by the underlying |twisted| routing mechanism that delegate its process to the main or root Mamba's controller (that is defined internally into the framework) that pass it to the Mamba's routing and templating system to locate, retrieve and render a response for the given request.

The response can be a HTML rendered page, text, a JSON structure, a XML Object or arbitrary binary data, that depends completely on the application and what the client is looking for. If Mamba can't locate a valid action or resource for the given request, a 404 response will be returned back.

Controllers route
=================

Every Mamba controller has to define a route for themselves, this route is their position in the web site path hierarchy and it **must** be a single path segment of the URL. A controller that doesn't define a controller route is attached to the main |twisted| Site object and becomes the root of the application. That means no Mamba's default special behaviour is going to be available for the site if we don't define it mannually in the controller that becomes the root.

.. note::

    Don't worry if you don't totally understand that, it will be clear later in this chapter.

The controller's route can be defined when we create the controller using the ``mamba-admin controller`` sub-command or just editing the resulting file with our text editor. The argument for the ``mamba-admin`` command line tool is ``--route=<our route>`` so for example, the command::

    $ mamba-admin controller --route=api webservice

Will create a new controller python script on ``application/controller/webservice.py`` with the following content:

.. sourcecode:: python

    # -*- encoding: utf-8 -*-
    # -*- mamba-file-type: mamba-controller -*-
    # Copyright (c) 2013 - damnwidget <damnwidget@localhost>

    """
    .. controller:: Webservice
        :platform: Linux
        :synopsis: None

    .. controllerauthor:: damnwidget <damnwidget@localhost>
    """

    from mamba.web.response import Ok
    from mamba.application import route
    from mamba.application import controller


    class Webservice(controller.Controller):
        """
        None
        """

        name = 'Webservice'
        __route__ = 'api'

        def __init__(self):
            """
            Put your initializarion code here
            """
            super(Webservice, self).__init__()

As you can see, the generated file already defines the controller's route as ``'api'`` but we can just modify that value to whatever other route that we want. If we use more than one single URL path segment the route is totally ignored and our controller is not registered in the system making it unavailable.

.. sourcecode:: python

    ...
    __route__ = 'api/socket'
    ...

The above example should end in the behaviour described above.

Controllers actions
===================

Controllers can define arbitrary routes with the ``@route`` decorator that finally callbacks the decorated method. Those routes can be static routes (that only defines a path) or dynamic routes (that defines a path and wildcards for parameters).

.. sourcecode:: python

    # static route example
    @route('/comments')
    def comments(self, request, **kwargs):
        ...

    # dynamic route example
    @route('/comments/<int:comment_id>')
    def read_comment(self, request, comment_id, **kwargs):
        ...

Controller actions can define more extensive route paths so we can for example register the following route for our ``Webservice`` example controller (defined in the last section):

.. sourcecode:: python

    ...
    @route('/contacts/add/<email>/<password>')
    def add_contact(self, request, email, password, **kwargs):
        contact = new Contact(email, password)
        contact.create()

In the above example our final route path (as will be invoked from the web client) is ``http://localhost/api/contacts/add/john_doe@gmail.com/ultrasecret``. This is:

================ ============= ==========================================================
Controller route Action route  Match
================ ============= ==========================================================
/api             /contacts/add {'email': 'john_doe@gmail.com', 'password': 'ultrasecret'}
================ ============= ==========================================================

.. seealso::

    :doc:`routing`

Mamba's default root
====================

Mamba defines internally a default root route that points always to the ``index.html`` template view. Sometimes we need a controller to become the root of our application because we want to develop a full backend REST service or for whatever other reasson. When we do that, we are going to override all the Mamba's auto insertion of **mambaerized** resources like CSS, LESS or JavaScript files.

If you are not going to use a frontend at all then you are just done, all is ok and you don't have to care about but if you are planning to use Mamba's templating system then you have to create a new index to recover the default root functionality.

First of all we have to create a new view for the controller using the ``mamba-admin view`` subcommand. Let's imagine we defined a controller that becomes the root resource in our application and we call it ``Main`` and we use the default ``root`` action method as the ``/`` or index route:

.. sourcecode:: python

    class Main(controller.Controller):

        name = 'Main'
        __route__ = ''

        def __init__(self):
            """
            Put your initialization code here
            """
            super(Main, self).__init__()

        @route('/')
        def root(self, request, **kwargs):
            Ok('I am the Main, hello world!')

Then we generate a new view for the root action using the ``mamba-admin`` command line tool::

    $ mamba-admin view root Main

This will generate a new file ``application/view/Main/root.html`` that will be our new index template for the whole application that inherits from the ``layout.html`` template. This view will know how to insert the **mambaerized** resources into our templates in automatic way.

Our last step is to just make a small change in the ``root`` action in the controller to make it render our new index:

.. sourcecode:: python

    from mamba.core import templating

    class Main(controller.Controller):

        name = 'Main'
        __route__ = ''

        def __init__(self):
            """
            Put your initialization code here
            """
            super(Main, self).__init__()
            self.template = templating.Template(controller=self)

        @route('/')
        def root(self, request, **kwargs):
            return Ok(self.template.render().encode('utf-8'))

.. note::

    If you don't know what a *mambaerized resource file* is, we recommend you to read the :doc:`../getting_started` document and come back here when you read it

Going asynchronous
==================

Mamba is just |twisted| and |twisted| is an asynchronous network framework. We can run operations asynchronous and return back callbacks from |twisted| deferreds as we do in any normal |twisted| application. We can do it always that we decorate a model method with the ``@transact`` decorator in our models.

.. sourcecode:: python

    from twisted.internet import defer

    from mamba.application import route
    from mamba.application.controller import Controller

    from application import controller
    from application.model.post import Post


    class Blog(Controller):
        """
        Blog controller
        """

        name = 'Blog'
        __route__ = 'blog'

        def __init__(self):
            """
            Put your initialization code here
            """
            super(Blog, self).__init__()

        @route('/<int:post_id>/comments', method=['GET', 'POST'])
        @defer.inlineCallbacks
        def root(self, request, post_id, **kwargs):
            """Return back the comments for the given post
            """

            comments = yield Post().comments
            defer.returnValue(comments)

We just used the |twisted|'s ``@defer.inlineCallbacks`` decorator to yield results from asynchronous operations and then we returned back the value using ``defer.returnValue``.

.. seealso::

    `Twisted: Introduction to Deferreds <http://twistedmatrix.com/documents/current/core/howto/defer-intro.html>`_, `Twisted: Deferred Reference <http://twistedmatrix.com/documents/current/core/howto/defer.html>`_, `Twisted: Generating Deferreds <http://twistedmatrix.com/documents/current/core/howto/gendefer.html>`_

Returning values from controller actions
========================================

Surely the reader already noticed that we use an ``Ok`` object as return from our controller actions. The :class:`~mamba.web.responses.Ok` class is one of the multiple built-in response objects that you can return from your application controllers.

Mamba defines 15 predefined types of response objects that set the content-type and other parameters of the HTTP response that our applications can return back to the web clients.

    * :class:`~mamba.web.response.Response` dummy base response object, we can use this object to create ad-hoc responses on demand. All the rest of responses inherits from this class
    * :class:`~mamba.web.response.Ok` - Ok 200 HTTP Response
    * :class:`~mamba.web.response.Created` - Ok 201 HTTP Response
    * :class:`~mamba.web.response.Unknown` - Unknown 209 HTTP Response (this HTTP code is not defined, mamba returns that when a route just returns None)
    * :class:`~mamba.web.response.MovedPermanently` - Ok 301 HTTP Response
    * :class:`~mamba.web.response.Found` - Ok 302 HTTP Response
    * :class:`~mamba.web.response.SeeOther` - Ok 303 HTTP Response
    * :class:`~mamba.web.response.BadRequest` - Error 400 HTTP Response
    * :class:`~mamba.web.response.Unauthorized` - Error 401 HTTP Response
    * :class:`~mamba.web.response.Forbidden` - Error 403 HTTP Response
    * :class:`~mamba.web.response.NotFound` - Error 404 HTTP Response
    * :class:`~mamba.web.response.Conflict` - Error 409 HTTP Response
    * :class:`~mamba.web.response.AlreadyExists` - Error 409 HTTP Response (Conflict found in POST)
    * :class:`~mamba.web.response.InternalServerError` - Internal Error 500 HTTP Response
    * :class:`~mamba.web.response.NotImplemented` - Error 501 HTTP Response

Mamba return back some of those codes by itself in some situations, for example, if we try to use a route that exists but in a different HTTP method, we get a :class:`~mamba.web.response.NotImplemented` response object.

You can return whatever of these objects from your controller. Mamba take care of rendering it correctly to the web client. You can also return dictionaries and other objects. Mamba will try to convert whatever object you return from a controller into a serializable JSON structure with a default 200 OK HTTP response code and an 'application/json' encoding.
