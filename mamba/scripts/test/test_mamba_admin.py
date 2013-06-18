
# Copyright (c) 2012 - 2013 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
Tests for mamba.scripts.mamba_admin and subcommands
"""

import os
import sys
import getpass
import datetime
from cStringIO import StringIO

from twisted.internet import utils, defer
from twisted.trial import unittest
from twisted.python import usage, filepath

from mamba.scripts import mamba_admin, commons
from mamba.scripts._project import Application
from mamba.scripts._view import ViewOptions, View
from mamba.scripts._model import ModelOptions, Model
from mamba.scripts._controller import ControllerOptions, Controller
from mamba.scripts._sql import (
    Sql, SqlConfigOptions, SqlCreateOptions, SqlDumpOptions, SqlResetOptions
)

# set me as True if you want to skip slow command line tests
# I dont think you want this set as True unless you are adding
# some tests to command line scripts
skip_command_line_tests = True


class MambaAdminTest(unittest.TestCase):

    def test_subcommands(self):

        config = mamba_admin.Options()

        subCommands = config.subCommands
        expectedOrder = [
            'application', 'sql', 'controller',
            'model', 'view', 'package', 'start', 'stop'
        ]

        for subCommand, expectedCommand in zip(subCommands, expectedOrder):
            name, shortcut, parserClass, documentation = subCommand
            self.assertEqual(name, expectedCommand)
            self.assertEqual(shortcut, None)


class MambaAdminApplicationTest(unittest.TestCase):

    def setUp(self):
        self.config = mamba_admin.ApplicationOptions()

    def test_wrong_number_of_args(self):
        self.assertRaises(usage.UsageError, self.config.parseOptions, ['-n'])

    def test_default_port(self):
        self.config.parseOptions(['test'])
        self.assertEqual(self.config['port'], 1936)

    def test_override_port(self):
        self.config.parseOptions(['--port', '8080', 'test'])
        self.assertEqual(self.config['port'], 8080)

    def test_default_version(self):
        self.config.parseOptions(['test'])
        self.assertEqual(self.config['app-version'], '1.0')

    def test_override_version(self):
        self.config.parseOptions(['--app-version', '0.0.1', 'test'])
        self.assertEqual(self.config['app-version'], '0.0.1')

    def test_default_file(self):
        self.config.parseOptions(['test'])
        self.assertEqual(self.config['configfile'], 'application.json')

    def test_default_description(self):
        self.config.parseOptions(['test'])
        self.assertEqual(self.config['description'], 'A new Mamba application')

    def test_override_description(self):
        self.config.parseOptions(['--description', 'Test Desc', 'test'])
        self.assertEqual(self.config['description'], 'Test Desc')

    def test_noquestion_is_not_set_by_default(self):
        self.config.parseOptions(['test'])
        self.assertEqual(self.config['noquestions'], 0)

    def test_override_noquestions(self):
        self.config.parseOptions(['-n', 'test'])
        self.assertEqual(self.config['noquestions'], 1)

    def test_default_logfile(self):
        self.config.parseOptions(['test'])
        self.assertEqual(self.config['logfile'], None)

    def test_override_logfile(self):
        self.config.parseOptions(['--logfile', 'test.log', 'test'])
        self.assertEqual(self.config['logfile'], 'test.log')

    def test_log_extension_for_logfile_by_default(self):
        self.config.parseOptions(['--logfile', 'test', 'test'])
        self.assertEqual(self.config['logfile'], 'test.log')

    def test_name_with_spaces_replace_to_underscores(self):
        self.config.parseOptions(['-n', 'spaces name'])
        self.assertEqual(self.config['name'], 'spaces_name')

    def test_name_with_non_alphanumeric_characters_are_removed(self):
        self.config.parseOptions(['-n', 'test/with.tons%of&non$alpha#chars@'])
        self.assertEqual(self.config['name'], 'testwithtonsofnonalphachars')


class ApplicationTest(unittest.TestCase):

    def setUp(self):
        def fake_exit(value):
            pass

        self.stdout = sys.stdout
        self.capture = StringIO()
        sys.stdout = self.capture

        self.exit = sys.exit
        sys.exit = fake_exit

    def tearDown(self):
        sys.stdout = self.stdout
        sys.exit = self.exit
        testdir = filepath.FilePath('test')
        testdir.remove()

    def test_generate_application(self):
        Application('Test', 'Test App', '1.0', ('app.json', None), 8080, True)
        self.assertTrue(filepath.exists('test/test.py'))
        self.assertTrue(filepath.exists('test/config/app.json'))
        self.assertTrue(filepath.exists('test/twisted/plugins/test_plugin.py'))
        self.assertTrue(filepath.exists('test/application'))
        self.assertTrue(filepath.exists('test/application/controller'))
        self.assertTrue(filepath.exists('test/application/model'))
        self.assertTrue(filepath.exists('test/application/view'))
        self.assertTrue(filepath.exists('test/application/view/templates'))
        self.assertTrue(filepath.exists('test/application/view/stylesheets'))
        self.assertTrue(
            filepath.exists('test/application/view/templates/layout.html')
        )


class MambaAdminSqlConfigureTest(unittest.TestCase):

    def setUp(self):
        self.config = SqlConfigOptions()

    def test_wrong_number_of_args(self):
        self.assertRaises(usage.UsageError, self.config.parseOptions, ['test'])

    def test_drop_table_and_create_if_not_exists_conflicts(self):
        self.assertRaises(
            usage.UsageError,
            self.config.parseOptions,
            ['--drop-table', '--create-if-not-exists']
        )

    def test_min_thread_can_not_be_less_or_equals_to_zero(self):
        self.assertRaises(
            usage.UsageError,
            self.config.parseOptions,
            ['--min-threads=0']
        )
        self.assertRaises(
            usage.UsageError,
            self.config.parseOptions,
            ['--min-threads=-1']
        )

    def test_max_threads_can_not_be_less_than_five_or_more_than_1024(self):
        self.assertRaises(
            usage.UsageError,
            self.config.parseOptions,
            ['--max-threads=4']
        )
        self.assertRaises(
            usage.UsageError,
            self.config.parseOptions,
            ['--max-threads=1025']
        )

    def test_backend_must_be_valid_on_hostname_or_username_options(self):
        self.assertRaises(
            usage.UsageError,
            self.config.parseOptions,
            ['--hostname=localhost', '--backend=test', '--database=test']
        )

    def test_database_should_be_passed_on_hostanme_or_username_options(self):
        self.assertRaises(
            usage.UsageError,
            self.config.parseOptions,
            ['--hostname=localhost', '--backend=sqlite']
        )

    def test_generate_uri(self):
        self.config.parseOptions([
            '--username', 'testuser', '--password', 'testpassword',
            '--backend', 'mysql', '--database', 'testdb'
        ])
        self.assertEqual(
            self.config['uri'],
            'mysql://testuser:testpassword@localhost/testdb'
        )

        self.config.parseOptions([
            '--username', 'testuser', '--password', 'testpassword',
            '--backend', 'postgres', '--database', 'testdb'
        ])
        self.assertEqual(
            self.config['uri'],
            'postgres://testuser:testpassword@localhost/testdb'
        )

        self.config.parseOptions([
            '--backend', 'sqlite', '--path', 'testdb'
        ])
        self.assertEqual(
            self.config['uri'],
            'sqlite:testdb'
        )


class MambaAdminSqlCreateTest(unittest.TestCase):

    def setUp(self):
        self.config = SqlCreateOptions()
        self.stdout = sys.stdout
        self.capture = StringIO()
        sys.stdout = self.capture

    def tearDown(self):
        sys.stdout = self.stdout

    def test_wrong_number_of_args(self):
        self.assertRaises(
            usage.UsageError, self.config.parseOptions, ['test', 'wrong'])

    def test_default_options(self):
        self.config.parseOptions(['test'])
        self.assertEqual(self.config['live'], 0)
        self.assertEqual(self.config['dump'], 0)

    def test_set_options_works(self):
        self.config.parseOptions(['-d', 'test'])
        self.assertEqual(self.config['dump'], 1)

    def test_dump_and_live_cant_be_together(self):

        commons.raw_input = lambda _: '0'

        self.config.parseOptions(['-d', '-l', 'test'])

        self.assertTrue(
            'What do you want to do. Dump the script or execute it?' in
            self.capture.getvalue()
        )
        self.assertTrue('Dump it' in self.capture.getvalue())
        self.assertTrue('Execute it' in self.capture.getvalue())


class SqlCreateTest(unittest.TestCase):

    def setUp(self):
        if skip_command_line_tests is True:
            raise unittest.SkipTest('skip_command_line_tests is set as True')

        self.config = SqlCreateOptions()
        self.stdout = sys.stdout
        self.capture = StringIO()
        sys.stdout = self.capture

    def tearDown(self):
        sys.stdout = self.stdout

    def test_use_outside_application_directory_fails(self):
        _test_use_outside_application_directory_fails(self)

    @defer.inlineCallbacks
    def test_sql_create_dump(self):

        result = yield utils.getProcessValue('mamba-admin', [], os.environ)
        if result == 1:
            raise unittest.SkipTest('mamba framework is not installed yet')

        currdir = os.getcwd()
        os.chdir('../mamba/test/dummy_app/')

        result = yield utils.getProcessOutput(
            'python',
            ['../../scripts/mamba_admin.py', 'sql', 'create', '--dump'],
            os.environ
        )

        self.assertTrue('CREATE TABLE IF NOT EXISTS dummy' in result)
        self.assertTrue('PRIMARY KEY(id)' in result)
        self.assertTrue('name VARCHAR' in result)
        self.assertTrue('id INTEGER' in result)

        os.chdir(currdir)

    @defer.inlineCallbacks
    def test_sql_create_file(self):

        result = yield utils.getProcessValue('mamba-admin', [], os.environ)
        if result == 1:
            raise unittest.SkipTest('mamba framework is not installed yet')

        currdir = os.getcwd()
        os.chdir('../mamba/test/dummy_app/')
        yield utils.getProcessOutput(
            'python',
            ['../../scripts/mamba_admin.py', 'sql', 'create', 'test'],
            os.environ
        )

        dump_file = filepath.FilePath('test.sql')
        self.assertTrue(dump_file.exists())
        self.assertTrue(dump_file.getsize() > 0)
        dump_file.remove()

        os.chdir(currdir)

    @defer.inlineCallbacks
    def test_sql_create_live(self):

        result = yield utils.getProcessValue('mamba-admin', [], os.environ)
        if result == 1:
            raise unittest.SkipTest('mamba framework is not installed yet')

        currdir = os.getcwd()
        os.chdir('../mamba/test/dummy_app/')

        cfg_file = filepath.FilePath('config/database.json')
        cfg_file_content = cfg_file.open('r').read()
        cfg_file_new = cfg_file_content.replace('dummy.db', 'dummy2.db')
        cfg_file.open('w').write(cfg_file_new)

        yield utils.getProcessOutput(
            'python', ['../../scripts/mamba_admin.py', 'sql', 'create', '-l'],
            os.environ
        )

        db_file = filepath.FilePath('db/dummy2.db')
        self.assertTrue(db_file.exists)
        db_file.remove()

        cfg_file.open('w').write(cfg_file_content)

        os.chdir(currdir)


class MambaAdminSqlDumpTest(unittest.TestCase):

    def setUp(self):
        self.config = SqlDumpOptions()
        self.stdout = sys.stdout
        self.capture = StringIO()
        sys.stdout = self.capture

    def tearDown(self):
        sys.stdout = self.stdout

    def test_wrong_number_of_args(self):
        self.assertRaises(
            usage.UsageError, self.config.parseOptions, ['test', 'wrong'])


class SqlDumpTest(unittest.TestCase):

    def setUp(self):
        if skip_command_line_tests is True:
            raise unittest.SkipTest('skip_command_line_tests is set as True')

        self.config = SqlDumpOptions()
        self.stdout = sys.stdout
        self.capture = StringIO()
        sys.stdout = self.capture

    def tearDown(self):
        sys.stdout = self.stdout

    def test_use_outside_application_directory_fails(self):
        _test_use_outside_application_directory_fails(self)

    @defer.inlineCallbacks
    def test_sql_dump(self):

        result = yield utils.getProcessValue('mamba-admin', [], os.environ)
        if result == 1:
            raise unittest.SkipTest('mamba framework is not installed yet')

        currdir = os.getcwd()
        os.chdir('../mamba/test/dummy_app')
        result = yield utils.getProcessOutput(
            'python', ['../../scripts/mamba_admin.py', 'sql', 'dump'],
            os.environ
        )

        self.assertTrue("INSERT INTO 'dummy'" in result)
        self.assertTrue("INSERT INTO 'stubing'" in result)
        self.assertTrue('Test row 1' in result)
        self.assertTrue('Test row 2' in result)
        self.assertTrue('Test row 3' in result)

        os.chdir(currdir)

    @defer.inlineCallbacks
    def test_sql_dump_to_file(self):

        #_check_mamba_admin_tool()
        result = yield utils.getProcessValue('mamba-admin', [], os.environ)
        if result == 1:
            raise unittest.SkipTest('mamba framework is not installed yet')

        currdir = os.getcwd()
        os.chdir('../mamba/test/dummy_app')
        yield utils.getProcessOutput(
            'python', ['../../scripts/mamba_admin.py', 'sql', 'dump', 'test'],
            os.environ
        )

        dump_file = filepath.FilePath('test.sql')
        self.assertTrue(dump_file.exists())
        self.assertTrue(dump_file.getsize() > 0)
        dump_file.remove()

        os.chdir(currdir)


class MambaAdminSqlResetTest(unittest.TestCase):

    def setUp(self):
        self.config = SqlResetOptions()
        self.stdout = sys.stdout
        self.capture = StringIO()
        sys.stdout = self.capture

    def tearDown(self):
        sys.stdout = self.stdout

    def test_wrong_number_of_args(self):
        self.assertRaises(
            usage.UsageError, self.config.parseOptions, ['test']
        )


class SqlResetTest(unittest.TestCase):

    @defer.inlineCallbacks
    def test_sql_reset(self):

        if skip_command_line_tests is True:
            raise unittest.SkipTest('skip_command_line_tests is set as True')

        result = yield utils.getProcessValue('mamba-admin', [], os.environ)
        if result == 1:
            raise unittest.SkipTest('mamba framework is not installed yet')

        currdir = os.getcwd()
        os.chdir('../mamba/test/dummy_app')
        db_file = filepath.FilePath('db/dummy.db')
        db_contents = db_file.open('rb').read()
        result = yield utils.getProcessOutput(
            'python',
            ['../../scripts/mamba_admin.py', 'sql', 'reset', '-n'],
            os.environ
        )

        self.assertEqual(
            result,
            'All the data in your database has been reset.\n')

        db_file.open('wb').write(db_contents)

        os.chdir(currdir)


class MambaAdminControllerTest(unittest.TestCase):

    def setUp(self):
        self.config = ControllerOptions()

    def test_wrong_number_of_args(self):
        self.assertRaises(
            usage.UsageError, self.config.parseOptions, ['test', 'wrong']
        )

    def test_name_camelize(self):
        self.config.parseOptions(['test_controller'])
        self.assertEqual(self.config['name'], 'TestController')

    def test_filename_lowerize_and_normalize(self):
        self.config.parseOptions(['Tes/t_controller$'])
        self.assertEqual(self.config['filename'], 'test_controller')
        self.assertEqual(self.config['name'], 'TestController')

    def test_email_validation(self):

        def fake_exit(value):
            pass

        exit = sys.exit
        sys.exit = fake_exit

        stdout = sys.stdout
        capture = StringIO()
        sys.stdout = capture

        self.config.parseOptions(['--email', 'no@valid', 'test_controller'])
        self.assertEqual(
            capture.getvalue(),
            'error: the given email address no@valid is not a valid RFC2822 '
            'email address, check http://www.rfc-editor.org/rfc/rfc2822.txt '
            'for very extended details\n'
        )

        sys.stdout = stdout
        sys.exit = exit

    def test_default_email(self):
        self.config.parseOptions(['test_controller'])
        self.assertEqual(
            self.config['email'],
            '{}@localhost'.format(getpass.getuser())
        )

    def test_default_plaform_is_linux(self):
        self.config.parseOptions(['test_controller'])
        self.assertEqual(self.config['platforms'], 'Linux')

    def test_default_route_is_empty(self):
        self.config.parseOptions(['test_controller'])
        self.assertEqual(self.config['route'], '')

    def test_default_synopsis_is_none(self):
        self.config.parseOptions(['test_controller'])
        self.assertEqual(self.config['description'], None)


class ControllerScriptTest(unittest.TestCase):

    def setUp(self):
        self.config = mamba_admin.Options()
        self.stdout = sys.stdout
        self.capture = StringIO()
        sys.stdout = self.capture

    def tearDown(self):
        sys.stdout = self.stdout

    def test_use_outside_application_directory_fails(self):
        _test_use_outside_application_directory_fails(self)

    def test_dump(self):
        Controller.process = lambda _: 0

        self.config.parseOptions(['controller', '--dump', 'test_controller'])
        controller = Controller(self.config)
        controller._dump_controller()
        self.assertEqual(
            self.capture.getvalue(),
            '\n\n'
            '# -*- encoding: utf-8 -*-\n'
            '# -*- mamba-file-type: mamba-controller -*-\n'
            '# Copyright (c) {year} - {author} <{author}@localhost>\n\n'
            '"""\n'
            '.. controller:: TestController\n'
            '    :platform: Linux\n'
            '    :synopsis: None\n\n'
            '.. controllerauthor:: {author} <{author}@localhost>\n'
            '"""\n\n'
            'from zope.interface import implements\n\n'
            'from mamba.web.response import Ok\n'
            'from mamba.core import interfaces\n'
            'from mamba.application import route\n'
            'from mamba.application import controller\n\n\n'
            'class TestController(controller.Controller):\n'
            '    """\n'
            '    None\n'
            '    """\n\n'
            '    implements(interfaces.IController)\n'
            '    name = \'TestController\'\n'
            '    __route__ = \'\'\n\n'
            '    def __init__(self):\n'
            '        """\n'
            '        Put your initializarion code here\n'
            '        """\n'
            '        super(TestController, self).__init__()\n\n'
            '    @route(\'/\')\n'
            '    def root(self, request, **kwargs):\n'
            '        return Ok(\'I am the TestController, hello world!\')'
            '\n\n'.format(
                year=datetime.datetime.now().year, author=getpass.getuser())
        )

    def test_write_file(self):
        Controller.process = lambda _: 0

        currdir = os.getcwd()
        os.chdir('../mamba/test/dummy_app/')

        self.config.parseOptions(['controller', 'test_controller'])
        controller = Controller(self.config)
        controller._write_controller()
        controller_file = filepath.FilePath(
            'application/controller/test_controller.py'
        )

        self.assertTrue(controller_file.exists())
        controller_file.remove()

        os.chdir(currdir)


class MambaAdminModelTest(unittest.TestCase):

    def setUp(self):
        self.config = ModelOptions()

    def test_wrong_number_of_args(self):
        self.assertRaises(
            usage.UsageError, self.config.parseOptions, ['0', '1', '2']
        )

    def test_name_camelize(self):
        self.config.parseOptions(['test_model', 'test'])
        self.assertEqual(self.config['name'], 'TestModel')

    def test_filename_lowerize_and_normalize(self):
        self.config.parseOptions(['Tes/t_model$', 'test'])
        self.assertEqual(self.config['filename'], 'test_model')
        self.assertEqual(self.config['name'], 'TestModel')

    def test_email_validation(self):

        def fake_exit(value):
            pass

        exit = sys.exit
        sys.exit = fake_exit

        stdout = sys.stdout
        capture = StringIO()
        sys.stdout = capture

        self.config.parseOptions(['--email', 'no@valid', 'test_model', 'test'])
        self.assertEqual(
            capture.getvalue(),
            'error: the given email address no@valid is not a valid RFC2822 '
            'email address, check http://www.rfc-editor.org/rfc/rfc2822.txt '
            'for very extended details\n'
        )

        sys.stdout = stdout
        sys.exit = exit

    def test_default_email(self):
        self.config.parseOptions(['test_model', 'test'])
        self.assertEqual(
            self.config['email'],
            '{}@localhost'.format(getpass.getuser())
        )

    def test_default_plaform_is_linux(self):
        self.config.parseOptions(['test_model', 'test'])
        self.assertEqual(self.config['platforms'], 'Linux')

    def test_default_synopsis_is_none(self):
        self.config.parseOptions(['test_model', 'test'])
        self.assertEqual(self.config['description'], None)


class ModelScriptTest(unittest.TestCase):

    def setUp(self):
        self.config = mamba_admin.Options()
        self.stdout = sys.stdout
        self.capture = StringIO()
        sys.stdout = self.capture

    def tearDown(self):
        sys.stdout = self.stdout

    def test_use_outside_application_directory_fails(self):
        _test_use_outside_application_directory_fails(self)

    def test_dump(self):
        Model.process = lambda _: 0

        self.config.parseOptions(['model', '--dump', 'test_model', 'test'])
        model = Model(self.config)
        model._dump_model()
        self.assertEqual(
            self.capture.getvalue(),
            '\n\n'
            '# -*- encoding: utf-8 -*-\n'
            '# -*- mamba-file-type: mamba-model -*-\n'
            '# Copyright (c) {year} - {author} <{author}@localhost>\n\n'
            '"""'
            '\n'
            '.. model:: TestModel\n'
            '    :plarform: Linux\n'
            '    :synopsis: None\n\n'
            '.. modelauthor:: {author} <{author}@localhost>\n'
            '"""\n\n'
            'from storm.locals import *\n\n'
            'from mamba.application import model\n\n\n'
            'class TestModel(model.Model):\n'
            '    """\n'
            '    None\n'
            '    """\n\n'
            '    __storm_table__ = \'test\'\n\n'
            '    id = Int(primary=True, unsigned=True)\n\n\n'.format(
                author=getpass.getuser(), year=datetime.datetime.now().year
            )
        )

    def test_write_file(self):
        Model.process = lambda _: 0

        currdir = os.getcwd()
        os.chdir('../mamba/test/dummy_app/')

        self.config.parseOptions(['model', 'test_model', 'test'])
        model = Model(self.config)
        model._write_model()
        model_file = filepath.FilePath(
            'application/model/test_model.py'
        )

        self.assertTrue(model_file.exists())
        model_file.remove()

        os.chdir(currdir)


class MambaAdminViewTest(unittest.TestCase):

    def setUp(self):
        self.config = ViewOptions()

    def test_wrong_number_of_args(self):
        self.assertRaises(
            usage.UsageError, self.config.parseOptions, ['0', '1', '2']
        )

    def test_name_camelize(self):
        self.config.parseOptions(['test_view', 'test'])
        self.assertEqual(self.config['name'], 'TestView')

    def test_filename_lowerize_and_normalize(self):
        self.config.parseOptions(['Tes/t_view$', 'test'])
        self.assertEqual(self.config['filename'], 'test_view')
        self.assertEqual(self.config['name'], 'TestView')

    def test_email_validation(self):

        def fake_exit(value):
            pass

        exit = sys.exit
        sys.exit = fake_exit

        stdout = sys.stdout
        capture = StringIO()
        sys.stdout = capture

        self.config.parseOptions(['--email', 'no@valid', 'test_model', 'test'])
        self.assertEqual(
            capture.getvalue(),
            'error: the given email address no@valid is not a valid RFC2822 '
            'email address, check http://www.rfc-editor.org/rfc/rfc2822.txt '
            'for very extended details\n'
        )

        sys.stdout = stdout
        sys.exit = exit

    def test_default_email(self):
        self.config.parseOptions(['test_model', 'test'])
        self.assertEqual(
            self.config['email'],
            '{}@localhost'.format(getpass.getuser())
        )

    def test_default_synopsis_is_none(self):
        self.config.parseOptions(['test_model', 'test'])
        self.assertEqual(self.config['description'], None)


class ViewScriptTest(unittest.TestCase):

    def setUp(self):
        self.config = mamba_admin.Options()
        self.stdout = sys.stdout
        self.capture = StringIO()
        sys.stdout = self.capture

    def tearDown(self):
        sys.stdout = self.stdout

    def test_use_outside_application_directory_fails(self):
        _test_use_outside_application_directory_fails(self)

    def test_dump(self):
        View.process = lambda _: 0

        self.config.parseOptions(['view', '--dump', 'test_model'])
        view = View(self.config)
        view._dump_view()
        self.assertTrue(
            '    <!--\n'
            '        Copyright (c) {year} - {author} <{author}@localhost>\n\n'
            '        view: TestModel\n'
            '            synopsis: None\n\n'
            '        viewauthor: {author} <{author}@localhost>\n'
            '    -->\n\n'
            '    <h2>It works!</h2>\n\n'.format(
                author=getpass.getuser(), year=datetime.datetime.now().year
            ) in self.capture.getvalue()
        )

    def test_write_file(self):
        View.process = lambda _: 0

        currdir = os.getcwd()
        os.chdir('../mamba/test/dummy_app/')

        self.config.parseOptions(['view', 'test_view'])
        view = View(self.config)
        view._write_view()
        view_file = filepath.FilePath(
            'application/view/templates/test_view.html'
        )

        self.assertTrue(view_file.exists())
        view_file.remove()

        os.chdir(currdir)

    def test_write_file_with_controller(self):
        View.process = lambda _: 0

        currdir = os.getcwd()
        os.chdir('../mamba/test/dummy_app/')

        self.config.parseOptions(['view', 'test_view', 'dummy'])
        view = View(self.config)
        view._write_view()
        view_file = filepath.FilePath(
            'application/view/Dummy/test_view.html'
        )

        self.assertTrue(view_file.exists())
        view_file.remove()

        os.chdir(currdir)


def _test_use_outside_application_directory_fails(self, dump_opt=False):

    def fake_exit(val):
        pass

    sys.exit = fake_exit

    if dump_opt is not False:
        self.config.parseOptions(['--dump'])

    sql = Sql(self.config)

    try:
        sql._handle_create_command()
    except UnboundLocalError:
        self.assertTrue(
            'error: make sure you are inside a mmaba '
            'application root directory and then run '
            'this command again' in self.capture.getvalue()
        )
