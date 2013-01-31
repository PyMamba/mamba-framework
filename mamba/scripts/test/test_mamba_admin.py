
# Copyright (c) 2012 - 2013 Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
Tests for mamba.scripts.mamba_admin and subcommands
"""

import os
import sys
import subprocess
from cStringIO import StringIO

from twisted.trial import unittest
from twisted.python import usage, filepath

from mamba.scripts import mamba_admin, commons
from mamba.scripts._project import Application
from mamba.scripts._sql import (
    Sql, SqlOptions, SqlConfigOptions, SqlCreateOptions
)


class MambaAdminTest(unittest.TestCase):

    def test_subcommands(self):

        config = mamba_admin.Options()

        subCommands = config.subCommands
        expectedOrder = [
            'application', 'sql', 'controller', 'model', 'view', 'entity',
            'test', 'start', 'stop'
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
        self.config.parseOptions(['-p', '8080', 'test'])
        self.assertEqual(self.config['port'], 8080)

    def test_default_version(self):
        self.config.parseOptions(['test'])
        self.assertEqual(self.config['app-version'], '1.0')

    def test_override_version(self):
        self.config.parseOptions(['-v', '0.0.1', 'test'])
        self.assertEqual(self.config['app-version'], '0.0.1')

    def test_default_file(self):
        self.config.parseOptions(['test'])
        self.assertEqual(self.config['configfile'], 'application.json')

    def test_override_file(self):
        self.config.parseOptions(['-f', 'test.json', 'test'])
        self.assertEqual(self.config['configfile'], 'test.json')

    def test_json_extension_for_file_by_default(self):
        self.config.parseOptions(['-f', 'test.cfg', 'test'])
        self.assertEqual(self.config['configfile'], 'test.cfg.json')

    def test_default_description(self):
        self.config.parseOptions(['test'])
        self.assertEqual(self.config['description'], 'A new Mamba application')

    def test_override_description(self):
        self.config.parseOptions(['-d', 'Test Desc', 'test'])
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
        self.config.parseOptions(['-l', 'test.log', 'test'])
        self.assertEqual(self.config['logfile'], 'test.log')

    def test_log_extension_for_logfile_by_default(self):
        self.config.parseOptions(['-l', 'test', 'test'])
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
        self.config = SqlCreateOptions()
        self.stdout = sys.stdout
        self.capture = StringIO()
        sys.stdout = self.capture

    def tearDown(self):
        sys.stdout = self.stdout

    def test_use_outside_application_directory_fails(self):

        def fake_exit(val):
            print val
            pass

        sys.exit = fake_exit

        self.config.parseOptions(['--dump'])
        sql = Sql(self.config)

        try:
            sql._handle_create_command()
        except UnboundLocalError:
            self.assertEqual(
                'error: make sure you are inside a mmaba application root '
                'directory and then run this command again',
                self.capture.getvalue().split('\n')[-3:-2][0]
            )
            # sys.exit(-1) :)
            self.assertEqual(
                '-1',
                self.capture.getvalue().split('\n')[-2:-1][0]
            )

    def test_sql_create_dump(self):

        currdir = os.getcwd()
        os.chdir('../mamba/test/dummy_app/')

        proc = subprocess.Popen(
            ['python',
                '../../scripts/mamba_admin.py', 'sql', 'create', '--dump'],
            stdout=subprocess.PIPE
        )

        script, ignore = proc.communicate()

        self.assertTrue('CREATE TABLE IF NOT EXISTS dummy' in script)
        self.assertTrue('PRIMARY KEY(id)' in script)
        self.assertTrue('name VARCHAR' in script)
        self.assertTrue('id INTEGER' in script)

        os.chdir(currdir)

    def test_sql_create_file(self):

        currdir = os.getcwd()
        os.chdir('../mamba/test/dummy_app/')
        subprocess.call(
            ['python', '../../scripts/mamba_admin.py', 'sql', 'create', 'test']

        )
        dump_file = filepath.FilePath('test.sql')
        self.assertTrue(dump_file.exists())
        dump_file.remove()

        os.chdir(currdir)

    def test_sql_create_live(self):

        currdir = os.getcwd()
        os.chdir('../mamba/test/dummy_app/')

        cfg_file = filepath.FilePath('config/database.json')
        cfg_file_content = cfg_file.open('r').read()
        cfg_file_new = cfg_file_content.replace('dummy.db', 'dummy2.db')
        cfg_file.open('w').write(cfg_file_new)

        subprocess.call(
            ['python', '../../scripts/mamba_admin.py', 'sql', 'create', '-l']
        )
        db_file = filepath.FilePath('db/dummy2.db')
        self.assertTrue(db_file.exists)
        db_file.remove()

        cfg_file.open('w').write(cfg_file_content)

        os.chdir(currdir)
