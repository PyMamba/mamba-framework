.. _getting_started;

Getting Started
===============

Ready to get started? This is a section for the impatient, and give you a very basic introduction about Mamba. If you are looking for detailed information about how it Mamba works go to :ref:`what_mamba_is` page. If what you are looking for is documentation about `Twisted <http://www.twistedmatrix.com>`_ just click on the link to go their main site.

In this section we are going to create first dummy mamba application to get familiar with the `mamba-admin` command line tool and the mamba's MVC model.

Generate the application
------------------------

First of all, we are going to generate our mamba application using the `mamba-admin` command line tool::

    $ mamba-admin application --description='Dummy Application' --app-version=1.0 --logfile='service.log' --port=8080 -n dummy
    Creating dummy directory...                                              [Ok]
    Generating application/ directory...                                     [Ok]
    Generating application/controller directory...                           [Ok]
    Generating application/model directory...                                [Ok]
    Generating application/view directory...                                 [Ok]
    Generating application/view/templates directory...                       [Ok]
    Generating application/view/stylesheets directory...                     [Ok]
    Generating twisted directory...                                          [Ok]
    Generating twisted/plugins directory...                                  [Ok]
    Generating static directory...                                           [Ok]
    Generating config directory...                                           [Ok]
    Writing Twisted plugin...                                                [Ok]
    Writing plugin factory...                                                [Ok]
    Writing mamba service...                                                 [Ok]
    Writing configuration file...                                            [Ok]
    Writing favicon.ico file...                                              [Ok]
    Writting layout.html template file...                                    [Ok]

This command just generates a new mamba application directory called **dummy** which contains all the necessary files to start working in our new application. The auto-generated application is already startable so we can just run our application using the **start** mamba admin subcommand inside the just generated directory::

    $ cd dummy
    $ mamba-admin start
    starting application dummy...                                            [Ok]

This will start the Twisted web server in the port 8080. If we redirect our browser to this port we should get a blank page like the one shown in the image below.

.. image:: _static/getting_started/getting_started_01.png


Adding some HTML content
------------------------

Now, we are going to add some HTML static content to our new mamba web application, to do that we have to edit the main Jinja2 template layout.html file in the view/templates directory.

.. note:: To get detailed information about the mamba MVC pattern and directory hierarchy refer to :ref:`MVC_and_hierarchy` page

For the purpose of this introduction we are using the *vim* text editor in the GNU/Linux interpreter directly but you can use whatever text editor you are comfortable with. When we first open the file we should get a common Jinja2 template file that looks like this:

.. code-block:: jinja

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

The default layout extends *root_page.html* layout that is used internally by mamba to add scripts and other components in automatic way into your applications.

.. warning:: If you want that mamba include for you all the *mambaerized* css and JavaScript files that you add to the *view/scripts* and *view/stylesheets* directory automatically, your layout **must** extends the *root_page.html* template or mamba should not add any script or css file that is present in those already mentioned directories. If you try to use the Jinja2 templating **super()** method in a block that should being inherited from *root_page.html* you are going to get back an unhandled exception from the Jinja2 templating system.

We are going to add the common HTML elements that all our pages will share in the layout.html template that mamba generated for us in the previous step but we are going to create an *index.html* template file just for our index page, in this way we can just inherit from our *layout.html* file from whatever other template we add to the site. We should add this code to the body block in the *layout.html* file:

.. code-block:: jinja

    {% extends "root_page.html" %}
    {% block head %}
        <!-- Put your head content here, without <head></head> tags -->
    {{ super() }}
    {% endblock %}
    {% block body %}
        <!-- Put your body content here, without <body></body> tags -->

        {% block navigation %}
        <div class="navigation">
            <ul class="nav">
                <li><a href="/index">Home</a></li>
                <li><a href="/about_us">About us</a></li>
                <li><a href="/contact">Contact</a></li>
            </ul>
        </div>
        {% endblock %}

        {% block content %}
        {% endblock %}

    {% endblock %}
    {% block scripts %}
        <!-- Put your loadable scripts here -->
    {{ super() }}
    {% endblock %}

Now we are going to generate our *index* template file using the *mamba-admin* command line tool::

    $ mamba-admin view --description='Index template for Dummy application' index

This will generate a new Jinja2 template file called *index.html* in the *view/templates* directory with the following content:

.. code-block:: jinja

    {% extends "layout.html" %}
    {% block content %}
    {{ super() }}

    <!--
        Copyright (c) 2013 - damnwidget <damnwidget@localhost>

        view: Index
            synopsis: Index template for Dummy application

        viewauthor: damnwidget <damnwidget@localhost>
    -->

    <h2>It works!</h2>

    {% endblock %}

.. note::

    In your case the copyright and view author information should be adjust to your environment user configuration, this is pretty OS dependant

If we refresh our browser window we should get the following unstyled HTML on it:

.. image:: _static/getting_started/getting_started_02.png

Congratulations, you rendered your first mamba template sucessfully!. Now we are going to make some changes to the index template and add a CSS file to style a bit our index page:

.. code-block:: jinja

    {% extends "layout.html" %}
        {% block content %}
        {{ super() }}

        <!--
            Copyright (c) 2013 - damnwidget <damnwidget@localhost>

            view: Index
                synopsis: Index template for Dummy application

            viewauthor: damnwidget <damnwidget@localhost>
        -->

        <div class="content">
            <h2>Welcome to the Dummy Site!</h2>
            <p>Snakes are so cute aren't it?.</p>
            <img src="http://www.pymamba.com/assets/logo.png" />
        </div>

        {% endblock %}


.. code-block:: css

    /*
     *  -*- mamba-file-type: mamba-css -*-
     */

    body {
        background-color: #fff;
        color: #333;
        display: block;
        font-family: "Helvetica Neue", Helvetica,Arial,sans-serif;
        font-size: 16px;
        line-height: 20px;
        margin: 0;
        padding-top: 40px;
        position: relative;
    }

    a {
        color: #717171;
    }

    .navigation {
        content: "";
        background-color: #fafafa;
        background-image: linear-gradient(to bottom, #fff, #f2f2f2);
        background-repeat: repeat x;
        border: 1px solid #d4d4d4;
        box-shadow: 0 1px 10px rgba(0,0,0,0.1);
        line-height: 0;
        left: 0;
        margin-bottom: 0;
        min-height: 40px;
        position: fixed;
        right: 0;
        top: 0;
    }

    .nav {
        display: block;
        float: left;
        left: 0;
        list-style: none;
        margin: 0 10px 0 0;
        padding: 0;
        position: relative;
    }

    .nav li {
        display: list-item;
        float: left;
        line-height: 20px;
        margin-left: 30px;
        margin-top: 8px;
    }

    .nav li a {
        text-decoration: none;
    }

    .nav li a:hover {
        color: #aab212;
    }

    .content {
        margin: 20px auto;
        width: 920px;
    }

    .content h2 {
        font-size: 40px;
        margin: 60px 0 10px;
        font-weight: 200;
    }

.. note::

    Mamba CSS files should add the **-*- mamba-file-type: mamba-css -*-** special comment to be automatically loaded by mamba on startup

This will give us the result that can be shown in the following screenshot:

.. image:: _static/getting_started/getting_started_03.png

.
