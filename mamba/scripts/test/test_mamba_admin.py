
# Copyright (c) 2012 - 2013 Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
Tests for mamba.scripts.mamba_admin and subcommands
"""

import sys
from cStringIO import StringIO

from twisted.python import usage, filepath
from twisted.trial import unittest

from mamba.scripts import mamba_admin
from mamba.scripts._project import Application
from mamba.scripts._sql import Sql, SqlConfigOptions


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


class ApplcationTest(unittest.TestCase):

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


class MambaAdminSqlTest(unittest.TestCase):

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
