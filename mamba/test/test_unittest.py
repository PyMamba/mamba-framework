
# Copyright (c) 2012 ~ 2014 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""Unit tests for unittesting module helper
"""

import os

from storm.store import Store
from twisted.trial import unittest
from twisted.python.threadpool import ThreadPool

from mamba.utils import config
from mamba.application.model import Model
from mamba.unittest import database_helpers


class DatabaseHelpersTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        Model.database = database_helpers.Database()

    def test_testable_database_engine_native(self):
        db = database_helpers.TestableDatabase()
        self.assertEqual(db.engine, database_helpers.ENGINE.NATIVE)

    def test_initialize_engine_native(self):
        config.Database('../mamba/test/dummy_app/config/database.json')
        current_dir = os.getcwd()
        os.chdir('../mamba/test/dummy_app')
        db = database_helpers.TestableDatabase()
        store = db.store()
        self.assertEqual(store.get_database()._filename, 'db/dummy.db')
        os.chdir(current_dir)

    def test_testable_database_engine_inmemory(self):
        engine = database_helpers.ENGINE.INMEMORY
        db = database_helpers.TestableDatabase(engine)
        self.assertEqual(db.engine, database_helpers.ENGINE.INMEMORY)

    def test_initialize_engine_memory(self):
        engine = database_helpers.ENGINE.INMEMORY
        db = database_helpers.TestableDatabase(engine)
        store = db.store()
        self.assertEqual(store.get_database()._filename, ':memory:')
        store.close()

    def test_testable_database_engine_persistent(self):
        engine = database_helpers.ENGINE.PERSISTENT
        db = database_helpers.TestableDatabase(engine)
        self.assertEqual(db.engine, database_helpers.ENGINE.PERSISTENT)

    def test_initialize_engine_persistent(self):
        engine = database_helpers.ENGINE.PERSISTENT
        db = database_helpers.TestableDatabase(engine)
        uri = database_helpers.global_zstorm.get_default_uris()['mamba'].split(
            '?foreign_keys=1'
        )[0].split('sqlite:')[1]
        store = db.store()
        self.assertEqual(store.get_database()._filename, uri)

    def test_prepare_model_for_test(self):
        model = Model()
        self.assertEqual(model.database.__class__, database_helpers.Database)
        database_helpers.prepare_model_for_test(model)
        self.assertEqual(
            model.database.__class__, database_helpers.TestableDatabase)

    def test_prepate_model_for_test_using_class(self):
        self.assertEqual(Model.database.__class__, database_helpers.Database)
        database_helpers.prepare_model_for_test(Model)
        self.assertEqual(
            Model.database.__class__, database_helpers.TestableDatabase)

    def test_database_is_started_defacto(self):
        config.Database('../mamba/test/dummy_app/config/database.json')
        model = Model()
        database_helpers.prepare_model_for_test(model)
        self.assertTrue(model.database.started)

    def test_database_stop(self):
        model = Model()
        database_helpers.prepare_model_for_test(model)
        self.assertTrue(model.database.started)
        model.database.stop()
        self.assertFalse(model.database.started)

    def test_store_return_valid_store(self):
        model = Model()
        database_helpers.prepare_model_for_test(model)
        store = model.database.store()
        self.assertIsInstance(store, Store)

    def test_model_transactor_uses_dummy_thread_pool(self):
        model = Model()
        self.assertIsInstance(model.transactor._threadpool, ThreadPool)
        database_helpers.prepare_model_for_test(model)
        self.assertIsInstance(
            model.transactor._threadpool, database_helpers.DummyThreadPool)
