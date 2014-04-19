
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
Tests for mamba.enterprise.database
"""

import functools
from sqlite3 import sqlite_version_info

from storm.locals import Store
from twisted.trial import unittest
from zope.component import getUtility
from storm.zope.interfaces import IZStorm
from storm.exceptions import DisconnectionError
from twisted.python.threadpool import ThreadPool
from doublex import Spy, ANY_ARG, assert_that, called


from mamba.utils import config
from mamba.core import GNU_LINUX
from mamba.enterprise import Database
from mamba.enterprise.common import NativeEnum
from mamba.application.model import ModelManager
from mamba.enterprise.database import AdapterFactory


def multiple_databases(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        uri = config.Database().uri
        config.Database().uri = {
            'mamba': 'sqlite:', 'mamba2': 'mysql://root@localhost/mamba'
        }
        result = func(*args, **kwargs)
        config.Database().uri = uri
        return result

    return wrapper


class DatabaseTest(unittest.TestCase):

    def setUp(self):
        config.Database('../mamba/test/application/config/database.json')
        config.Database().uri = "sqlite:///db/dummy.db"
        self.database = Database(self.get_pool(), True)

    def tearDown(self):
        self.database.pool.stop()

    def get_commons_for_dump(self):
        import sys
        sys.path.append('../mamba/test/dummy_app')
        mgr = ModelManager()
        if GNU_LINUX:
            self.addCleanup(mgr.notifier.loseConnection)

        from mamba import Model
        from mamba.test.test_model import DummyThreadPool, DatabaseModuleError
        try:
            threadpool = DummyThreadPool()
            database = Database(threadpool, True)
            Model.database = database

            store = database.store()
            store.execute(
                'CREATE TABLE IF NOT EXISTS `dummy` ('
                '    id INTEGER PRIMARY KEY, name TEXT'
                ')'
            )
            store.execute(
                'CREATE TABLE IF NOT EXISTS `stubing` ('
                '   id INTEGER PRIMARY KEY, name TEXT'
                ')'
            )
            store.commit()
        except DatabaseModuleError as error:
            raise unittest.SkipTest(error)

        return mgr

    def get_pool(self):

        with Spy() as pool:
            pool.start(ANY_ARG)
            pool.stop(ANY_ARG)

        return pool

    def test_database_initial_name_is_database_pool(self):

        database = Database(testing=True)
        self.assertEqual(database.pool.name, 'DatabasePool')

    def test_databse_initial_pool_size_is_five_and_twenty_five(self):

        database = Database(testing=True)
        self.assertEqual(database.pool.min, 5)
        self.assertEqual(database.pool.max, 20)

    def test_database_initial_pool_size_min_negative_fail_assertion(self):

        self.assertRaises(AssertionError, ThreadPool, -1)

    def test_database_initial_size_min_greater_than_max_fail_assertion(self):

        self.assertRaises(AssertionError, ThreadPool, 30)

    def test_database_start(self):

        self.assertFalse(self.database.started)
        self.database.start()

        self.assertTrue(self.database.started)

    def test_database_stop(self):

        self.assertFalse(self.database.started)
        self.database.start()
        self.assertTrue(self.database.started)

        self.database.stop()
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

    def test_database_backend(self):
        self.assertEqual(self.database.backend, 'sqlite')

    @multiple_databases
    def test_database_multiple_backend(self):
        self.assertEqual(type(self.database.backend), list)
        self.assertEqual(self.database.backend[0], {'mamba2': 'mysql'})
        self.assertEqual(self.database.backend[1], {'mamba': 'sqlite'})

    def test_database_host(self):
        self.assertEqual(self.database.host, None)

    @multiple_databases
    def test_database_multiple_host(self):
        self.assertEqual(type(self.database.host), list)
        self.assertEqual(self.database.host[0], {'mamba2': 'localhost'})
        self.assertEqual(self.database.host[1], {'mamba': None})

    def test_database_database(self):
        self.assertEqual(self.database.database, None)

    @multiple_databases
    def test_database_multiple_database(self):
        self.assertEqual(type(self.database.database), list)
        self.assertEqual(self.database.database[0], {'mamba2': 'mamba'})
        self.assertEqual(self.database.database[1], {'mamba': None})

    def test_patch_sqlite_uris(self):
        if sqlite_version_info >= (3, 6, 19):
            self.assertTrue('foreign_keys=1' in config.Database().uri)

    @multiple_databases
    def test_patch_multiple_sqlite_uris(self):
        self.assertFalse('foreign_keys=1' in config.Database().uri['mamba'])
        self.database._patch_sqlite_uris()
        if sqlite_version_info >= (3, 6, 19):
            self.assertTrue('foreign_keys=1' in config.Database().uri['mamba'])

    def test_zstorm_default_uri(self):
        zstorm = getUtility(IZStorm)
        zstorm._default_uris = {}
        self.database._set_zstorm_default_uris(zstorm)
        self.assertEqual(
            zstorm.get_default_uris(), {'mamba': config.Database().uri})

    @multiple_databases
    def test_multiple_zstorm_default_uri(self):
        zstorm = getUtility(IZStorm)
        self.database._set_zstorm_default_uris(zstorm)
        self.assertEqual(zstorm.get_default_uris(), config.Database().uri)

    def test_database_dump(self):
        mgr = self.get_commons_for_dump()

        mgr.load('../mamba/test/dummy_app/application/model/dummy.py')
        mgr.load('../mamba/test/dummy_app/application/model/stubing.py')
        sql = self.database.dump(mgr)
        self.assertTrue('CREATE TABLE IF NOT EXISTS dummy (\n' in sql)
        self.assertTrue('  id integer,\n' in sql)
        self.assertTrue('  name varchar NOT NULL,\n' in sql)
        self.assertTrue('  PRIMARY KEY(id)\n);\n\n' in sql)
        self.assertTrue('CREATE TABLE IF NOT EXISTS stubing (\n' in sql)
        self.assertTrue('  id integer,\n' in sql)
        self.assertTrue('  name varchar NOT NULL,\n' in sql)
        self.assertTrue('  PRIMARY KEY(id)\n);\n' in sql)

        self.flushLoggedErrors()
        self.database.store().reset()

    def test_database_not_dump_mamba_schema_false(self):
        mgr = self.get_commons_for_dump()

        mgr.load('../mamba/test/dummy_app/application/model/dummy.py')
        mgr.load('../mamba/test/dummy_app/application/model/stubing.py')
        mgr.load(
            '../mamba/test/dummy_app/application/model/dummy_not_on_schema.py'

        )
        sql = self.database.dump(mgr)
        self.assertTrue('CREATE TABLE IF NOT EXISTS dummy (\n' in sql)
        self.assertTrue('  name varchar NOT NULL,\n' in sql)
        self.assertTrue('  id integer,\n' in sql)
        self.assertTrue('  PRIMARY KEY(id)\n);\n\n' in sql)
        self.assertTrue('CREATE TABLE IF NOT EXISTS stubing (\n' in sql)
        self.assertTrue('  id integer,\n' in sql)
        self.assertTrue('  name varchar NOT NULL,\n' in sql)
        self.assertTrue('  PRIMARY KEY(id)\n);\n' in sql)
        self.assertTrue('dummy_not_on_schema' not in sql)

        self.flushLoggedErrors()
        self.database.store().reset()

    def test_database_dump_data(self):
        config.Database('../mamba/test/dummy_app/config/database.json')
        mgr = self.get_commons_for_dump()

        import os
        currdir = os.getcwd()
        os.chdir('../mamba/test/dummy_app/')

        mgr.load('../mamba/test/dummy_app/application/model/dummy.py')
        mgr.load('../mamba/test/dummy_app/application/model/stubing.py')
        sql = self.database.dump(mgr, full=True)
        self.assertTrue("INSERT INTO 'dummy'" in sql)
        self.assertTrue("INSERT INTO 'stubing'" in sql)
        self.assertTrue('Test row 1' in sql)
        self.assertTrue('Test row 2' in sql)
        self.assertTrue('Test row 3' in sql)

        os.chdir(currdir)

    def test_database_reset(self):
        mgr = self.get_commons_for_dump()

        mgr.load('../mamba/test/dummy_app/application/model/dummy.py')
        mgr.load('../mamba/test/dummy_app/application/model/stubing.py')
        sql = self.database.reset(mgr)
        self.assertTrue('DROP TABLE IF EXISTS dummy;' in sql)
        self.assertTrue('DROP TABLE IF EXISTS stubing;' in sql)

    def test_database_reset_mamba_schema_false(self):
        mgr = self.get_commons_for_dump()

        mgr.load('../mamba/test/dummy_app/application/model/dummy.py')
        mgr.load('../mamba/test/dummy_app/application/model/stubing.py')
        mgr.load(
            '../mamba/test/dummy_app/application/model/dummy_not_on_schema.py'
        )
        sql = self.database.reset(mgr)
        self.assertTrue('DROP TABLE IF EXISTS dummy;' in sql)
        self.assertTrue('DROP TABLE IF EXISTS stubing;' in sql)
        self.assertTrue('dummy_not_on_schema' not in sql)

    def test_database_reset_mysql(self):
        cfg = config.Database('../mamba/test/dummy_app/config/database.json')
        cfg.uri = cfg.uri.replace('sqlite:', 'mysql://a:b@c/d')
        mgr = self.get_commons_for_dump()

        mgr.load('../mamba/test/dummy_app/application/model/dummy.py')
        mgr.load('../mamba/test/dummy_app/application/model/stubing.py')
        sql = self.database.reset(mgr)
        self.assertTrue('DROP TABLE IF EXISTS `dummy`;' in sql)
        self.assertTrue('DROP TABLE IF EXISTS `stubing`;' in sql)

    def test_database_reset_mysql_mamba_schema_false(self):
        cfg = config.Database('../mamba/test/dummy_app/config/database.json')
        cfg.uri = cfg.uri.replace('sqlite:', 'mysql://a:b@c/d')
        mgr = self.get_commons_for_dump()

        mgr.load('../mamba/test/dummy_app/application/model/dummy.py')
        mgr.load('../mamba/test/dummy_app/application/model/stubing.py')
        mgr.load(
            '../mamba/test/dummy_app/application/model/dummy_not_on_schema.py'
        )
        sql = self.database.reset(mgr)
        self.assertTrue('DROP TABLE IF EXISTS `dummy`;' in sql)
        self.assertTrue('DROP TABLE IF EXISTS `stubing`;' in sql)
        self.assertTrue('dummy_not_on_schema' not in sql)

    def test_database_reset_postgres(self):
        cfg = config.Database('../mamba/test/dummy_app/config/database.json')
        cfg.uri = cfg.uri.replace('sqlite:', 'postgres://a:b@c/d')
        mgr = self.get_commons_for_dump()

        mgr.load('../mamba/test/dummy_app/application/model/dummy.py')
        mgr.load('../mamba/test/dummy_app/application/model/stubing.py')
        sql = self.database.reset(mgr)
        self.assertTrue('DROP TABLE IF EXISTS dummy RESTRICT;' in sql)
        self.assertTrue('DROP TABLE IF EXISTS stubing RESTRICT;' in sql)

    def test_database_reset_postgres_mamba_schema_false(self):
        cfg = config.Database('../mamba/test/dummy_app/config/database.json')
        cfg.uri = cfg.uri.replace('sqlite:', 'postgres://a:b@c/d')
        mgr = self.get_commons_for_dump()

        mgr.load('../mamba/test/dummy_app/application/model/dummy.py')
        mgr.load('../mamba/test/dummy_app/application/model/stubing.py')
        sql = self.database.reset(mgr)
        self.assertTrue('DROP TABLE IF EXISTS dummy RESTRICT;' in sql)
        self.assertTrue('DROP TABLE IF EXISTS stubing RESTRICT;' in sql)
        self.assertTrue('dummy_not_on_schema' not in sql)

    def test_ensure_connect_called_when_ensure_connect_is_true(self):

        def _ensure_connect():
            raise RuntimeError

        self.database._ensure_connect = _ensure_connect
        self.assertRaises(
            RuntimeError, self.database.store, ensure_connect=True)

    def test_ensure_connect_calls_execute_and_commit(self):

        getUtility_spy, store = self._prepare_store_spy()

        from mamba.enterprise import database
        _getUtility = database.getUtility
        database.getUtility = getUtility_spy

        self.database.store(ensure_connect=True)
        assert_that(store.execute, called().with_args('SELECT 1').times(1))
        assert_that(store.commit, called().times(1))

        database.getUtility = _getUtility

    def test_ensure_connect_calls_rollback_on_disconnectionerror(self):

        getUtility_spy, store = self._prepare_store_spy(True)

        from mamba.enterprise import database
        _getUtility = database.getUtility
        database.getUtility = getUtility_spy

        self.database.store(ensure_connect=True)
        assert_that(store.execute, called().with_args('SELECT 1').times(1))
        assert_that(store.rollback, called().times(1))
        assert_that(store.commit, called().times(0))

        database.getUtility = _getUtility

    def _prepare_store_spy(self, raises_exception=False):

        with Spy() as store:
            getUtility_spy = lambda _: {'mamba': store}
            if raises_exception is True:
                store.execute(ANY_ARG).raises(DisconnectionError)

        return getUtility_spy, store


class NativeEnumTest(unittest.TestCase):

    def test_enum(self):
        column = NativeEnum(set={'foo', 'bar'}, default='foo')
        self.assertEqual(column._variable_kwargs['_set'], set(['foo', 'bar']))

        class EnumTest(object):
            __storm_table__ = 'testtable'
            prop1 = NativeEnum(set={'foo', 'bar'}, default='foo', primary=True)

        obj = EnumTest()
        self.assertEqual(obj.prop1, 'foo')
        obj.prop1 = 'bar'
        self.assertEqual(obj.prop1, 'bar')

        self.assertRaises(ValueError, setattr, obj, "prop1", "baz")
        self.assertRaises(ValueError, setattr, obj, "prop1", 1)


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
