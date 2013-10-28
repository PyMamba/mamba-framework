.. _routing:

=======================
The mamba routing guide
=======================

Mamba uses a routing engine similar to the ones found in Flask and Bottle. Of course you can register the same route path for those seven different HTTP methods

    * GET
    * POST
    * PUT
    * DELETE
    * OPTIONS
    * PATCH
    * HEAD

.. note::

    The default HTTP method is 'GET'.

Routes are defined in controllers using the ``@route``  decorator:

.. sourcecode:: python

    @route('/test', method='GET')
    def test(self, request, **kwargs):
        return Ok('I am a test!')

The decorated function has to accept all the positional arguments ``self`` and ``request``, the request argument is a low level |twisted| argument that is used internally by the routing system.

We can pass whatever argument we want to the route and access them using the ``kwargs`` dictionary. There is another way to register routes with arguments (that should be validated before fire the route callback) that we will review later in this chapter.

We can define that the route should be available for all the HTTP methods that we want just passing a tuple or a list of HTTP methods in the decorator.

.. sourcecode:: python

    @route('/test', method=('GET', 'POST'))
    def test(self, request, **kwargs):
        return Ok('I am a test!')

Controllers and routes
======================

In mamba there are two types of routes:

    1. Static routes
    2. Controller routes

The first one is used for mamba to locate and render templates that does not depends of a controller, those are, templates that are full frontend based like an static HTML page or a main HTML page that loads JavaScript to create `single page applications <http://en.wikipedia.org/wiki/Single-page_application>`_ using `AngularJS <http://www.angularjs.org/>`_ or whatever other library or framework.

The second one is used to create relationships between routes and actions in our application controllers. Those actions can end in some template rendering, some acces to the database, some communication with external services or whatever other action that we can think on.

Static routes
-------------

In mamba there is always a main static route tied to the web site root page that will point always to the index template.

.. note::

    This default behaviour can be overriden using controllers.

To create new static routes to other templates you only have to place a hyperlink in your HTML pointing to the new route and cretae a new template with the same name than the route in the ``application.view.templates`` directory. If for example your new route is ``http://localhost/about_us`` the template should be ``application/view/templates/about_us.html``.

Static routes has one limitation, they can't be nested in path hierarchies. So you can't define a static route that links to ``http://localhost/some_path/some_static_template``

That's because mamba doesn't know how to follow route to the ``some_path`` without a controller that define routes to do it.

.. note::

    The exposed above is an implementation decission. Mamba uses |twisted| web as primary component in order to run and render our web sites. |twisted| use ``twisted.web.resource.Resource`` class instances in to execute any logic that our web site needs, we always need an instance of this class to render our pages. Mamba take care of abstract this but it maintains itself flexible enough to make the developer able to override any mamba's specific behaviour.

    With this in mind, mamba does not allow the user code to define actions without a valid |twisted| resource, controllers are an abstraction of those |twisted| resources and they can be interchanged if needed. That means, an experienced |twisted| developer can bypass the mamba's routing system at all and use controllers as pure |twisted| resources or even use |twisted| resources as first class citizens.

.. seealso::

    :doc:`view`

Controller routes
-----------------

We have to diferenciate between the controller ``route`` and the controller actions:

    1. The controller ``route`` is the base path where the controller lives. If this route is a void string, then this controller override the default static route to the index page that we discuss about in the :ref:`Controllers and routes` section. If the controller route is for example `api` then all the routes to controller actions that the controller defines should really pont to ``http://localhost/api/<action>``
    2. The controller actions are regular methods that are decorated with the ``@route`` decorator and become unique URL entry points into our application.

A controller can have only one route but it can have as many actions as is needed. Only one controller can override the page index, if you define more than one controller with an empty string as it's route, then only one of them (in random way really) should be known by the routing system hidding the others completely.

.. seealso::

    :doc:`controller`

Controller actions
==================

Mamba distinguishes between two types of routes, static and dynamic routes. Static routes are all those routes that defines only a path part, for example:

.. sourcecode:: python

    @route('/blog')

Dynamic routes in the other hand, contains one or more *wildcards*:

.. sourcecode:: python

    @route('/blog/<post_id>')

Wildcards
---------

There are three type of wildcards on mamba:

    1. **Int** wildcard, that matches digits and cast them to integers
    2. **Float** wildcard, that macthes a decimal number and converts it to float
    3. **untyped** wildcards, that matches whatever other type of argument as strings

The wildcard consist in a name enclosed in angle brackets for untype wildcars or a type followed by a colon and a name enclosed in angle brackets if we are going to define numeric arguments.

.. sourcecode:: python

    # untyped wildcard
    @route('/run/<action>')
    def run(self, request, action, **kwargs):
        ...

    # int wildcard
    @route('/run/<action>/<int:post_id>')
    def run(self, request, action, post_id, **kwargs):
        ...

    # float wildcard
    @route('/sum/<float:amount>')
    def run(self, request, amount, **kwargs):
        ...

Wildcards names should be unique for a given route and must be a valid python identifier because they are going to be used as keyword arguments in the request callback when the routing system dispatch them.

Following the latest examples, the route ``/run/<action>`` matches:

    ==============  ===================
    **Path**        **Result**
    ==============  ===================
    /run/close      {'action': 'close'}
    /run/close/     {'action': 'close'}
    /run/close/bar  Doesn't match
    /run/           Doesn't match
    /run            Doesn't match
    ==============  ===================

If the decorated method does not define a positional argument that match the wildcard name, we can always get it using the **kwargs** dictionary:

.. sourcecode:: python

    @route('/run')
    def run(self, request, **kwargs):
        return Ok(kwargs.get('action'))

Although this is totally valid, we should use explicit argument definition in our methods to be more semantic.

Of course you can decide to don't use wildcards at all and just pass arguments to your actions in a traditional way with form encoding for POST and URIs for GET and you will be totally able to access all those arguments through the **kwargs** dictionary. Mamba give you the tool, but you decide how to use it.

|
