
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
Tests for mamba.enterprise.database
"""

from twisted.trial import unittest
from twisted.python.threadpool import ThreadPool
from doublex import Spy, assert_that, called, ANY_ARG

from storm.locals import Store, Int, Unicode

from mamba.utils import config
from mamba.enterprise import Database
from mamba.enterprise.database import AdapterFactory


class DatabaseTest(unittest.TestCase):

    def setUp(self):
        config.Database().load(
            '../mamba/test/application/config/database.json'
        )
        self.database = Database(self.get_pool())

    def tearDown(self):
        self.database.pool.stop()

    def get_pool(self):

        with Spy() as pool:
            pool.start(ANY_ARG)
            pool.stop(ANY_ARG)

        return pool

    def test_database_initial_name_is_database_pool(self):

        database = Database()
        self.assertEqual(database.pool.name, 'DatabasePool')

    def test_databse_initial_pool_size_is_five_and_twenty_five(self):

        database = Database()
        self.assertEqual(database.pool.min, 5)
        self.assertEqual(database.pool.max, 20)

    def test_database_initial_pool_size_min_negative_fail_assertion(self):

        self.assertRaises(AssertionError, ThreadPool, -1)

    def test_database_initial_size_min_greater_than_max_fail_assertion(self):

        self.assertRaises(AssertionError, ThreadPool, 30)

    def test_database_start(self):

        self.assertFalse(self.database.started)
        self.database.start()

        assert_that(self.database.pool.start, called().times(1))
        self.assertTrue(self.database.started)

    def test_database_start_returns_if_is_already_started(self):

        self.assertFalse(self.database.started)

        self.database.start()
        self.database.start()

        assert_that(self.database.pool.start, called().times(1))
        self.assertTrue(self.database.started)

    def test_database_stop(self):

        self.assertFalse(self.database.started)
        self.database.start()
        assert_that(self.database.pool.start, called().times(1))
        self.assertTrue(self.database.started)

        self.database.stop()
        assert_that(self.database.pool.stop, called().times(1))
        self.assertFalse(self.database.started)

    def test_database_stop_returns_if_is_already_stopped(self):

        self.assertFalse(self.database.started)
        self.database.start()
        assert_that(self.database.pool.start, called().times(1))
        self.assertTrue(self.database.started)

        self.database.stop()
        self.database.stop()
        assert_that(self.database.pool.stop, called().times(1))
        self.assertFalse(self.database.started)

    def test_database_adjust_size(self):

        self.database.pool = ThreadPool(0, 10)

        self.database.adjust_poolsize(4, 20)
        self.assertEqual(self.database.pool.min, 4)
        self.assertEqual(self.database.pool.max, 20)

    def test_database_adjust_size_min_negative_fail_assertion(self):

        self.database.pool = ThreadPool(0, 10)
        self.assertRaises(AssertionError, self.database.adjust_poolsize, -1)

    def test_database_adjust_size_min_greater_than_max_fail_assertion(self):

        self.database.pool = ThreadPool(0, 10)
        self.assertRaises(AssertionError, self.database.adjust_poolsize, 20)

    def test_database_store(self):
        store = self.database.store()
        self.assertIsInstance(store, Store)


class AdapterFactoryTest(unittest.TestCase):

    def get_adapter_for_scheme(self, scheme):
        if scheme == 'sqlite':
            from mamba.enterprise.sqlite import SQLite
            return AdapterFactory('sqlite', None).produce(), SQLite
        elif scheme == 'mysql':
            from mamba.enterprise.mysql import MySQL
            return AdapterFactory('mysql', None).produce(), MySQL
        else:
            from mamba.enterprise.postgres import PostgreSQL
            return AdapterFactory('postgres', None).produce(), PostgreSQL

    def test_sqlite_adapter(self):
        factory, instance = self.get_adapter_for_scheme('sqlite')
        self.assertIsInstance(factory, instance)

    def test_mysql_adapter(self):
        factory, instance = self.get_adapter_for_scheme('mysql')
        self.assertIsInstance(factory, instance)

    def test_postgres_adapter(self):
        factory, instance = self.get_adapter_for_scheme('postgres')
        self.assertIsInstance(factory, instance)