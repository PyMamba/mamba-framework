
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
Tests for mamba.application.model
"""

import tempfile
import functools

from storm.uri import URI
from twisted.trial import unittest
from twisted.python import filepath
from storm.locals import Int, Unicode
from storm.twisted.testing import FakeThreadPool
from twisted.internet.defer import inlineCallbacks

from mamba import Model
from mamba import Database
from mamba.utils import config
from mamba.core import interfaces
from mamba.enterprise.mysql import MySQLMissingPrimaryKey, MySQL
from mamba.enterprise.sqlite import SQLiteMissingPrimaryKey, SQLite
from mamba.enterprise.postgres import PostgreSQLMissingPrimaryKey, PostgreSQL


def common_config(
        engine='sqlite:', existance=True, restrict=True, cascade=False):
    """Decorator for common config needed for SQL engine testing"""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            db_config = tempfile.NamedTemporaryFile(delete=False)
            db_config.write('''
                {
                    "uri": "%s",
                    "min_threads": 5,
                    "max_threads": 20,
                    "auto_adjust_pool_size": false,
                    "create_table_behaviours": {
                        "create_if_not_exists": %s,
                        "drop_table": false
                    },
                    "drop_table_behaviours": {
                        "drop_if_exists": %s,
                        "restrict": %s,
                        "cascade": %s
                    }
                }
            ''' % (
                engine,
                'true' if existance else 'false',
                'true' if existance else 'false',
                'true' if restrict else 'false',
                'true' if cascade else 'false')
            )
            db_config.close()

            config.Database(db_config.name)
            assert(config.Database().loaded)

            result = func(*args, **kwargs)

            config.Database(
                '../mamba/test/application/config/database.json'
            )
            filepath.FilePath(db_config.name).remove()

            return result

        return wrapper

    return decorator


class ModelTest(unittest.TestCase):

    def setUp(self):

        threadpool = DummyThreadPool()
        self.database = Database(threadpool)
        Model.database = self.database

        store = self.database.store()
        store.execute(
            'CREATE TABLE IF NOT EXISTS `dummy` ('
            '    id INTEGER PRIMARY KEY, name TEXT'
            ')'
        )
        store.commit()

    def tearDown(self):
        self.flushLoggedErrors()

    def get_adapter(self):

        return DummyModel().get_adapter()

    def test_model_create(self):
        dummy = DummyModel('Dummy')
        dummy.create()

        self.assertEqual(dummy.id, 1)

    @inlineCallbacks
    def test_model_read(self):
        dummy = yield DummyModel().read(1)
        self.assertEqual(dummy.id, 1)
        self.assertEqual(dummy.name, u'Dummy')

    @inlineCallbacks
    def test_model_update(self):
        dummy = yield DummyModel().read(1)
        dummy.name = u'Fellas'
        dummy.update()

        del(dummy)
        dummy = yield DummyModel().read(1)
        self.assertEqual(dummy.id, 1)
        self.assertEqual(dummy.name, u'Fellas')

    def test_model_delete(self):
        dummy = yield DummyModel().read(1)
        dummy.delete()

        store = self.database.store()
        self.assertTrue(len(store.find(DummyModel)) == 0)

    def test_model_dump_table(self):
        dummy = DummyModel()
        script = dummy.dump_table()

        self.assertTrue('CREATE TABLE IF NOT EXISTS dummy' in script)
        self.assertTrue('PRIMARY KEY(id)' in script)
        self.assertTrue('name VARCHAR' in script)
        self.assertTrue('id INTEGER' in script)

    @common_config(engine='mysql:')
    def test_model_dump_table_with_mysql(self):

        dummy = DummyModel()
        script = dummy.dump_table()

        self.assertTrue('CREATE TABLE IF NOT EXISTS `dummy`' in script)
        self.assertTrue('PRIMARY KEY(`id`)' in script)
        self.assertTrue('`name` varchar(64)' in script)
        self.assertTrue('`id` int UNSIGNED AUTO_INCREMENT' in script)
        self.assertTrue('ENGINE=InnoDB' in script)
        self.assertTrue('DEFAULT CHARSET=utf8' in script)

    @common_config(engine='postgres:')
    def test_model_dump_table_with_postgres(self):

        dummy = DummyModel()
        script = dummy.dump_table()

        self.assertTrue('CREATE TABLE IF NOT EXISTS \'dummy\'' in script)
        self.assertTrue('PRIMARY KEY(\'id\')' in script)
        self.assertTrue('\'name\' varchar(64)' in script)
        self.assertTrue('\'id\' serial' in script)

    @inlineCallbacks
    def test_model_create_table(self):
        dummy = DummyModel()
        yield dummy.create_table()

        store = dummy.database.store(dummy)

        self.assertEqual(
            store.execute('''
                SELECT name
                FROM sqlite_master
                WHERE type="table"
                ORDER BY name
            ''').get_one()[0],
            u'dummy'
        )

    def test_get_uri(self):
        dummy = DummyModel()
        self.assertEqual(dummy.get_uri().scheme, URI('sqlite:').scheme)

    def test_get_adapter(self):
        dummy = DummyModel()
        adapter = dummy.get_adapter()
        self.assertTrue(interfaces.IMambaSQL.providedBy(adapter))

    def test_sqlite_raises_missing_primary_key_exception(self):

        dummy = NotPrimaryModel()

        sqlite = SQLite(dummy)
        self.assertRaises(SQLiteMissingPrimaryKey, sqlite.detect_primary_key)

    def test_mysql_raises_missing_primary_key_exception(self):

        dummy = NotPrimaryModel()

        mysql = MySQL(dummy)
        self.assertRaises(MySQLMissingPrimaryKey, mysql.detect_primary_key)

    def test_postgres_raises_missing_primary_key_exception(self):

        dummy = NotPrimaryModel()

        postgres = PostgreSQL(dummy)
        self.assertRaises(
            PostgreSQLMissingPrimaryKey, postgres.detect_primary_key
        )

    def test_sqlite_drop_table(self):

        adapter = self.get_adapter()
        self.assertEqual(adapter.drop_table(), 'DROP TABLE IF EXISTS dummy')

    @common_config(existance=False)
    def test_sqlite_drop_table_no_existance(self):

        adapter = self.get_adapter()
        self.assertEqual(adapter.drop_table(), 'DROP TABLE dummy')

    @common_config(engine='mysql:')
    def test_mysql_drop_table(self):

        adapter = self.get_adapter()
        self.assertEqual(adapter.drop_table(), "DROP TABLE IF EXISTS `dummy`")

    @common_config(engine='mysql:', existance=False)
    def test_mysql_drop_table_no_existance(self):

        adapter = self.get_adapter()
        self.assertEqual(adapter.drop_table(), "DROP TABLE `dummy`")

    @common_config(engine='postgres:')
    def test_postgres_drop_table(self):

        adapter = self.get_adapter()
        self.assertEqual(
            adapter.drop_table(), "DROP TABLE IF EXISTS 'dummy' RESTRICT"
        )

    @common_config(engine='postgres:', existance=False)
    def test_postgres_drop_table_no_existance(self):

        adapter = self.get_adapter()
        self.assertEqual(adapter.drop_table(), "DROP TABLE 'dummy' RESTRICT")

    @common_config(engine='postgres:', cascade=True)
    def test_postgres_drop_table_on_cascade(self):

        adapter = self.get_adapter()
        self.assertEqual(
            adapter.drop_table(),
            "DROP TABLE IF EXISTS 'dummy' RESTRICT CASCADE"
        )

    @common_config(engine='postgres:', cascade=False, restrict=False)
    def test_postgres_drop_table_no_restrict(self):

        adapter = self.get_adapter()
        self.assertEqual(
            adapter.drop_table(),
            "DROP TABLE IF EXISTS 'dummy'"
        )

    @common_config(engine='postgres:', cascade=True, restrict=False)
    def test_postgres_drop_table_no_restrict_on_cascade(self):

        adapter = self.get_adapter()
        self.assertEqual(
            adapter.drop_table(),
            "DROP TABLE IF EXISTS 'dummy' CASCADE"
        )


class DummyModel(Model):
    """Dummy Model for testing purposes"""

    __storm_table__ = 'dummy'
    id = Int(primary=True, auto_increment=True, unsigned=True)
    name = Unicode(size=64, allow_none=False)

    def __init__(self, name=None):
        super(DummyModel, self).__init__()

        if name is not None:
            self.name = unicode(name)


class NotPrimaryModel(Model):
    """Failing model for testing purposes"""

    __storm_table__ = 'dummy'
    id = Int(primary=False)
    name = Unicode(size=64, allow_none=False)
    _storm_columns = {}


class DummyThreadPool(FakeThreadPool):

    def start(self):
        pass

    def stop(self):
        pass
