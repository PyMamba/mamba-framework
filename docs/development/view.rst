.. _view:

====================
The mamba view guide
====================

Mamba uses |jinja2|_ as template engine. Jinja2 is a modern and designer friendly templating language for Python, modelled after Django's templates. It is fast, widely used and secure with optional sandboxed template execution environment.

Jinja2 Documentation
====================

Jinja2 has it's own (and extensive) documentation, mamba take cares of the initialization of the common contexts and loaders so you don't have to take care yourself.

The |jinja2| documentation is available in it's `project web site <http://jinja.pocoo.org/docs/>`_, we recommend you visit their documentation.

Mamba templating
================

Mamba implements its own wrapper around |jinja2| templating engine to integrate it with mamba routing and controllers systems.

In mamba, the only thing that you need to create and render a new template is create a |jinja2| template file into ``application/view/templates`` directory and point to it with your browsers or link it in another of your application pages.

Mamba define a default root template internally called ``root_page.html`` that is needed for the framework to insert the web resources that we add to the ``stylesheets`` and ``scripts`` directories into ``application/view``. The layout that all the views in your application share inherit directly from this internal template.

Files inside the ``stylesheets`` and ``scripts`` directory must define an special file header for make it able to being automatic loaded by the styles and scripts managers and inserted in all your templates. Those special file headers are::

    /*
     * -*- mamba-file-type: mamba-css -*-
     */

for css files and::

    /*
     * -*- mamba-file-type: mamba-javascript -*-
     */

for JavaScript ones.

When we generate a new mamba application with the ``mamba-admin`` command line tool, it creates a default ``layout.html`` file that is located inside the ``application/view`` directory. This file can be used as common layout for all your application pages and it **must** inherit directly from ``root_page.html``.

The default content of the basic layout is as follows:

.. sourcecode:: jinja

    {% extends "root_page.html" %}
    {% block head %}
        <!-- Put your head content here, without <head></head> tags -->
    {{ super() }}
    {% endblock %}
    {% block body %}
        <!-- Put your body content here, without <body></body> tags -->
    {% endblock %}
    {% block scripts %}
        <!-- Put your loadable scripts here -->
    {{ super() }}
    {% endblock %}

We want to define all the common elements in our web site or web application in this file and then create new templates that inherit from this file. To create a new template for our application index we can do it with the ``mamba-admin`` command tool::

    $ mamba-admin view index

The command above will generate a new ``index.html`` template file inside ``application/view/templates`` directory with the following content:

.. sourcecode:: jinja

    {% extends "layout.html" %}
        {% block content %}
        {{ super() }}

        <!--
            Copyright (c) 2013 - damnwidget <damnwidget@localhost>

            view: Index
                synopsis: None

            viewauthor: damnwidget <damnwidget@localhost>
        -->

        <h2>It works!</h2>

        {% endblock %}

As you can see, this new template file inherits from ``layout.html``, as we already defined our web site layout we have only to take care of the *content* of this especific template or page, in this way we don't need to rewrite unnecesary HTML code in every template in our web site.

We can create as many template files as we want for our application but those templates are just static templates their content is really inmutable. Sometimes this us just what you want because you are creating a single page application for example and what you need is just load some JavaScript files that really takes care of all the frontend related actions.

To generate dynamic content for our templates we need controllers and routes that call actions in those controllers and then render a view based in our template files.

The mamba Template class
========================

The way that mamba controllers have to render our templates is just using the :class:`mamba.core.templating.Template` class. We can render whatever template that we need instanciating those classes and calling their ``render`` method with the arguments that we need.

.. sourcecode:: python

    ...
    from mamba.core import interfaces, templating
    ...

    class DummyController(Controller):
        """Just a dummy example controller
        """

        name = 'Dummy'
        __route__ = 'dummy'

        def __init__(self):
            super(DummyController, self).__init__()
            self.template = templating.Template(controller=self)

When we pass ``self`` as the ``controller`` argument to the constructor we are telling mamba to look for templates also in the controller templates directory. Every template that is inside this directory hides whatever other template that is located in the general templates directory (``application/view/templates``) that has the same name.

The controller templates directory
----------------------------------

The controller's templates directory is a directory inside ``application/view`` with the same name than the controller, so following our previous example, the ``DummyController`` templates directory will be ``application/view/DummyController``.

If for example we want to render the index (or root) of a given controller route we only have to create a new |jinja2| template file with the same name than the action function. So if our ``DummyController`` index action is called ``root`` we have to create a ``root.html`` file inside ``application/view/DummyController``, we can do it of course using the ``mamba-admin`` command line tool::

    $ mamba-admin view root DummyController

The command is exactly the same than before but we add a second argument that is the name of the controller that we want to create this template for. Let's imagine that we generate that ``root.html`` file inside the ``DummyController`` templates directory with the following content:

.. sourcecode:: jinja

    {% extends "layout.html" %}
        {% block content %}
        {{ super() }}

        <h2>Hello {{ name }}!</h2>

        {% endblock %}


The python action function in the controller that renders this view should look like:

.. sourcecode:: python

    @route('/')
    def root(self, request, **kwargs):
        """Renders the DummyController main page
        """

        template_args = {'name': 'Mamba'}
        return Ok(self.template.render(**template_args).encode('utf-8'))

Our web site will render *Hello Mamba!*

Shared template arguments
-------------------------

Sometimes we are really going to need to share some global data between different controllers and templates, for example on which section of the web site we are to correctly draw a navigation menu.

In those cases we need somewhere to place global common data that we can share between controllers to correctly render our views, we can usually place this code in two common places:

    * The ``application/__init__.py``
    * The ``application/controller/__init__.py``

This is the case of the mamba's main page navigation bar for example. Mamba main site define a tipical bootstrap nav bar like:

.. sourcecode:: jinja

    <ul class="nav">
      {% if menu %}
        {% macro selected_li(path, label, active, available, caller) -%}
        <li {% if active %} class="active" {% endif %}><a {% if not available %} data-toggle="modal" data-target="#notYetModal" {% endif %} href="{{ path }}">{{ label }}</a></li>
        {%- endmacro %}
        {% for link in menu_options %}
          {% call selected_li(link.path, link.label, link.active, link.available) %}
          {% endcall %}
        {% endfor %}
      {% else %}
        <li class="active"><a href="/index">Home</a></li>
        <li><a href="#gettingstart">Get started</a></li>
        <li><a href="#docs">Documentation</a></li>
        <li><a href="download">Download</a></li>
        <li><a href="#blog">Blog</a></li>
        <li><a href="contact">Contact</a></li>
      {% endif %}
    </ul>

To correctly render the web site we need to know in which page we are now and which pages are available from where we are. To do that we added a global structure in the ``applicaiton/controller/__init__.py`` file that we can use from whatever controller:

.. sourcecode:: python

    # Controllers should be placed here

    """
    Some helper functions and stuff here to make our life easier
    """

    HOME, GET_STARTED, DOCUMENTATION, DOWNLOAD, BLOG, CONTACT = range(6)

    template_args = {
        'menu': True,
        'menu_options': [
            {'path': '/', 'label': 'Home', 'active': False, 'available': True},
            {
                'path': 'gettingstart', 'label': 'Get started',
                'active': False, 'available': True
            },
            {
                'path': 'docs', 'label': 'Documentation',
                'active': False, 'available': True
            },
            {
                'path': 'download', 'label': 'Download',
                'active': False, 'available': True
            },
            {'path': 'blog', 'label': 'Blog', 'active': False, 'available': True},
            {
                'path': 'contact', 'label': 'Contact',
                'active': True, 'available': True
            },
        ]
    }


    def toggle_menu(menu_entry):
        """
        Toggle all the active state menus that are not the given menu entry to
        inactive and set the given one as active

        :param menu_entry: the menu entry to active
        :type menu_entry: dict
        """

        menu = template_args['menu_options'][menu_entry]
        if menu['available'] is False:
            return

        for item in template_args['menu_options']:
            if item['active']:
                if item == menu:
                    continue

                item['active'] = False

        menu['active'] = True

In this way in the downloads page controller we can set this structure as needed:

.. sourcecode:: python

    from application import controller

    class Downloads(Controller):
    ...
        @route('/', method=['GET', 'POST'])
        @defer.inlineCallbacks
        def root(self, request, **kwargs):
            """Renders downloads main page
            """

            controller.toggle_menu(controller.DOWNLOAD)
            template_args = controller.template_args

            template_args['releases'] = yield Release().last_release_files()
            template_args['old_releases'] = yield Release().old_release_files()

            defer.returnValue(
                Ok(self.template.render(**template_args).encode('utf-8')))
    ...

We fill the ``controller.template_args`` using the function ``toggle_menu`` with the right location before pass it as part of the arguments to the template ``render`` method.

.. note::

    The full code of the mamba web site can be found under the GPLv3 License at `https://github.com/DamnWidget/BlackMamba <https://github.com/DamnWidget/BlackMamba>`_

Rendering global templates from controller actions
--------------------------------------------------

We can pass a template name as the first argument (or as template keyword argument) to the template ``render`` method. If we passed ``self`` as value of the ``controller`` argument when you instantiate the ``Template`` object, then mamba should try to load it from the controller's templates directory and if can't find it then it will look in the global templates directory.

If mamba can't find any template with that name then it raises a :class:`core.templating.NotConfigured` exception.

Auto compiling LESS scripts
===========================

Mamba can auto-compile `LESS <http://lesscss.org/>`_ scripts if the `lessc` tool has been istalled on the system as its available to the user that is running the mamba application.
In case that the `lessc` tool is not installed on the system, the raw contents of the less file are returned as fallback.

To add a |less| resource to our application we should just place the |less| file into the `application/view/stylesheets` directory with the following header:

.. sourcecode:: css

    /*
     * -*- mamba-file-type: mamba-less -*-
     */
     ...

Mamba will try to compile the |less| scripts that are placed in that directory and return it back as already ccompiled CSS contents to the browser in total transparent way.

|less| auto-compilation when lessc is not available
---------------------------------------------------

In environments where `lessc` is not available, Heroku for example, we can set the configuration option `lessjs` in `config/application.json` with the exact file name of the `less.js` script that we want to use.
Mamba will insert the |less| JavaScript version in the main layout for us.

.. note ::

    The full list of available `less.js` script versions can be found in GitHub: https://github.com/less/less.js/tree/master/dist



|
