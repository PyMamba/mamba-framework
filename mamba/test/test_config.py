
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

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
        self.assertEqual(config.Database().min_threads, 0)
        self.assertEqual(config.Database().max_threads, 10)

    def test_database_fallback_if_previous_loaded_was_ok(self):
        bad_file = tempfile.NamedTemporaryFile(delete=False)
        bad_file.write('[}')
        bad_file.close()

        config.Database('../mamba/test/application/config/database.json')
        config.Database(bad_file.name)
        self.assertFalse(config.Database().loaded)
        self.assertEqual(config.Database().uri, 'sqlite:')
        self.assertEqual(config.Database().min_threads, 0)
        self.assertEqual(config.Database().max_threads, 10)

        filepath.FilePath(bad_file.name).remove()

    def test_database_dont_fallback_on_no_existent_when_valid_previous(self):
        config.Database('../mamba/test/dummy_app/config/database.json')
        config.Database('unknown.json')
        self.assertTrue(config.Database().loaded)
        self.assertEqual(config.Database().min_threads, 5)
        config.Database()
        self.assertTrue(config.Database().loaded)
        self.assertEqual(config.Database().min_threads, 5)
