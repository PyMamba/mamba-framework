.. unit_tests:


============
Unit testing
============

Each unit test will test a single functionallity of the system. Unit tests are automated and should run with no human intervention. The output of an unit test should be **pass** or **fail**. All the tests on mamba al gathered in a single test suite and can run as a single batch.

Howto running tests
-------------------

Mamba uses Twisted's `Trial <http://twistedmatrix.com/trac/wiki/TwistedTrial>`_ tool to run unit tests. To run the test suite you have to cd into the mamba root directory and run the trial tool:

    $ trial mamba

You can also execute the `tests` bash script that runs `trial mamba` in the background:

    $ ./tests

Adding new tests
----------------

You never add a new module to mamba without adding a batch of unit tests for the module as well. You never commit any code **until you make sure** that all the tests pass, so that means all the tests should be green when you run `trial mamba` in the root of the project.

If you commit code that breaks the unit test suite ever you can be *hunted down* by other developers so make sure your code follow the guidelines and pass the tests.

You have to add unit tests for your module and code because in this way other developers can check if their own changes to other parts of the code affects in any way your modules just runnign the test suite.

Tests go into dedicated test packages, normally `mamba/test/` for framework tests and `mamba/scripts/test` for the `mamba-admin` command line tool. Tests should be named as `test_module.py`. If the module is part of a core system like *web* you can add the tests directly into the `mamba/test/test_web.py` file.

Mamba tests cases should inherit from `twisted.trial.unittest.TestCase` instead of the standard library `unittest.TestCase`.

Twisted test implementation guidelines
--------------------------------------

The next section is exact to `twisted unit testing documentation <http://twistedmatrix.com/documents/current/core/development/policy/test-standard.html>`_, mamba is based on twisted itself so the same guidelines are applied to the implementation of unit tests. Those guidelines has been copied (and modified for convenience in some cases) as is from the current twisted version documentation.

Real I/O
~~~~~~~~

Most unit tests should avoid performing real, platform-implemented I/O operations. Real I/O is slow, unreliable, and unwieldy. When implementing a protocol, twisted.test.proto_helpers.StringTransport can be used instead of a real TCP transport. StringTransport is fast, deterministic, and can easily be used to exercise all possible network behaviors.

.. note::

    Mamba is a web applications framework but can be used to create any type of applications that you can create using twisted itself, it's very common in mamba to implement custom protocols and implement mashup solutions that integrate servers and clients using different protocols.

Real Time
~~~~~~~~~

Most unit tests should also avoid waiting for real time to pass. Unit tests which construct and advance a `twisted.internet.task.Clock <http://twistedmatrix.com/documents/13.0.0/api/twisted.internet.task.Clock.html>`_ are fast and deterministic.

Skipping tests
~~~~~~~~~~~~~~

Trial implements some custom features in top of the stadard `unittest` library that are designed to encougare developers to add new tests. One common situation is that a test exercises some optional functionality: maybe it depends upon certain external libraries being available, maybe it only works on certain operating systems. The important common factor is that nobody considers these limitations to be a bug.

To make it easy to test as much as possible, some tests may be skipped in certain situations. Individual test cases can raise the SkipTest exception to indicate that they should be skipped, and the remainder of the test is not run. In the summary (the very last thing printed, at the bottom of the test output) the test is counted as a "*skip*" instead of a "*success*" or "*fail*". This should be used inside a conditional which looks for the necessary prerequisites:

.. sourcecode:: python

    # code extracted from 'mamba/test/test_controller.py'
    class ControllerManagerTest(unittest.TestCase):
        ...
        def test_inotifier_provided_by_controller_manager(self):
            if not GNU_LINUX:
                raise unittest.SkipTest('File monitoring only available on Linux')
            self.assertTrue(INotifier.providedBy(self.mgr))

You can also set the `.skip` attribute on the method, with a string to indicate why the test is being skipped. This is convenient for temporarily turning off a test case, but it can also be set conditionally (by manipulating the class attributes after they've been defined):

.. sourcecode:: python

    class SomeThingTests(unittest.TestCase):
        def test_thing(self):
            dotest()
        test_thing.skip = "disabled locally"


.. sourcecode:: python

    class MyTestCase(unittest.TestCase):
        def test_one(self):
            ...
        def test_thing(self):
            dotest()

    if not haveThing:
        MyTestCase.test_thing.im_func.skip = "cannot test without Thing"
        # but test_one() will still run


Finally, you can turn off an entire TestCase at once by setting the .skip attribute on the class. If you organize your tests by the functionality they depend upon, this is a convenient way to disable just the tests which cannot be run.

.. sourcecode:: python

    class TCPTestCase(unittest.TestCase):
        ...
    class SSLTestCase(unittest.TestCase):
        if not haveSSL:
            skip = "cannot test without SSL support"
        # but TCPTestCase will still run


Associating test cases with source files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Please add a test-case-name tag to the source file that is covered by your new test. This is a comment at the beginning of the file which looks like one of the following:

.. sourcecode:: python

    # -*- test-case-name: mamba.test.test_web -*-

or

.. sourcecode:: python

    #!/usr/bin/env python
    # -*- test-case-name: mamba.test.test_web -*-

This format is understood by emacs to mark "*File Variables*". The intention is to accept `test-case-name` anywhere emacs would on the first or second line of the file (but not in the File Variables: block that emacs accepts at the end of the file). If you need to define other emacs file variables, you can either put them in the File Variables: block or use a semicolon-separated list of variable definitions:

.. sourcecode:: python

    # -*- test-case-name: mamba.test.test_web; fill-column: 75; -*-

If the code is exercised by multiple test cases, those may be marked by using a comma-separated list of tests, as follows: (NOTE: not all tools can handle this yet.. `trial --testmodule` does, though)

.. sourcecode:: python

    # -*- test-case-name: mamba.test.test_web,mamba.test.test_resource -*-

The test-case-name tag will allow `trial --testmodule twisted/dir/myfile.py` to determine which test cases need to be run to exercise the code in `myfile.py`. Several tools (as well as `twisted-dev.el's F9 command <http://launchpad.net/twisted-emacs>`_) use this to automatically run the right tests.

Sublime Text
~~~~~~~~~~~~

A plugin is being developed for integrate this on Sublime Text versions 2 and 3

Must-read links
---------------

`Tips for writing tests for Twisted code <http://twistedmatrix.com/documents/current/core/howto/testing.html>`_

|
|