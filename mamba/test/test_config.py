
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
Tests for mamba.utils.config
"""

import tempfile

from twisted.trial import unittest
from twisted.python import filepath

from mamba.utils import config


class DatabaseTest(unittest.TestCase):

    def tearDown(self):
        config.Database('default')

    def test_database_load(self):
        config.Database('../mamba/test/dummy_app/config/database.json')
        self.assertTrue(config.Database().loaded)
        self.assertEqual(config.Database().uri, 'sqlite:///db/dummy.db')
        self.assertEqual(config.Database().min_threads, 5)
        self.assertEqual(config.Database().max_threads, 20)

    def test_database_fallback_on_no_existent_file(self):
        self.assertFalse(config.Database().loaded)
        self.assertEqual(config.Database().uri, 'sqlite:')
        self.assertEqual(config.Database().min_threads, 5)
        self.assertEqual(config.Database().max_threads, 20)

    def test_database_fallback_if_previous_loaded_was_ok(self):
        import sys
        from cStringIO import StringIO
        stdout = sys.stdout
        sys.stdout = StringIO()

        bad_file = tempfile.NamedTemporaryFile(delete=False)
        bad_file.write('[}')
        bad_file.close()

        config.Database('../mamba/test/application/config/database.json')
        config.Database(bad_file.name)
        self.assertFalse(config.Database().loaded)
        self.assertEqual(config.Database().uri, 'sqlite:')
        self.assertEqual(config.Database().min_threads, 5)
        self.assertEqual(config.Database().max_threads, 20)

        filepath.FilePath(bad_file.name).remove()
        sys.stdout = stdout

    def test_database_dont_fallback_on_no_existent_when_valid_previous(self):
        config.Database('../mamba/test/dummy_app/config/database.json')
        config.Database('unknown.json')
        self.assertTrue(config.Database().loaded)
        self.assertEqual(config.Database().min_threads, 5)
        config.Database()
        self.assertTrue(config.Database().loaded)
        self.assertEqual(config.Database().min_threads, 5)


class ApplicationTest(unittest.TestCase):
    """Fallback functionallity already tested on Database Tests
    """

    def tearDown(self):
        config.Application('default')

    def test_application_load(self):
        config.Application('../mamba/test/dummy_app/config/application.json')
        self.assertTrue(config.Application().loaded)
        self.assertEqual(config.Application().name, 'dummy')
        self.assertEqual(
            config.Application().description,
            'This is a Dummy application just for testing purposes'
        )
        self.assertEqual(config.Application().version, '0.1.2')
        self.assertEqual(config.Application().port, 8080)
        self.assertEqual(config.Application().logfile, None)

    def test_fallback_works(self):
        self.assertFalse(config.Application().loaded)
        self.assertEqual(config.Application().name, None)
        self.assertEqual(config.Application().port, None)
        self.assertEqual(config.Application().description, None)
        self.assertEqual(config.Application().doctype, 'html')


class InstalledPackagesTest(unittest.TestCase):
    """Fallback is default on InstalledPackages
    """

    def tearDown(self):
        config.InstalledPackages('default')

    def test_intalled_packages_laod(self):
        config.InstalledPackages(
            '../mamba/test/dummy_app/config/installed_packages.json')
        self.assertFalse(config.InstalledPackages().loaded)
        self.assertEqual(config.InstalledPackages().packages, {})
