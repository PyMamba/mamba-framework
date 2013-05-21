.. _resuability:

Mamba reusability
=================

Mamba applications, controllers, templates, models and components can be reused all packed in an importable application or in individual way using the mamba reusability system.

The motivation for supporting this system in mamba is pretty straightforward, as Python developers, sometimes we need a common feature like being able to send emails to our users using some type of SMTP service in our applications. Mamba itself is not able to send emails because it doesn't know how to do it, this is an implemenatation design decission as we think sending emails is not part of the responsabilities of the framework but it's a pretty standard need for several web related projects, but not all.

The need to reuse the same type of features in several of our projects show us the need to add some way of easy-code-reusability system in mamba, and now here we are.

How it works?
-------------

Mamba is able to include and reuse applications and components from and to your applications in several ways, for example, it can search for shared code in the user (that is running mamba-admin) configuration directory if she is not allowed to install Python applications in the global Python installation directory.

Although we are allow to ruese any Python application just adding a package directly inside our `application` directory (and it works and has nothing wrong), mamba uses the `mamba-admin` command line tool to package (or unpackage) mamba based applications and create reusable mamba packages. Those packages can be installed globally or per-user using `mamba-admin package` subcommand.

Mamba also allow us to create reusable models, controllers, views or components (like small libraries or third party software) using `model`, `controller` `view` or `component` subcommand from `mamba-admin` command line tool. Those 'individual' pieces of code can be installed globally or per-user using the `mamba-admin package` subcommand.

Packing an application
~~~~~~~~~~~~~~~~~~~~~~

TODO

Packing a component
~~~~~~~~~~~~~~~~~~~

TODO

Unpacking
~~~~~~~~~

TODO

Using the per-user reusability hook
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the preferred way to reuse common code in shared environments where we are sharing the physical machine resources with other users like in a web hosting service.


