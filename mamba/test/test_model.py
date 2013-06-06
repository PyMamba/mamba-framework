
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
Tests for mamba.application.model
"""

import sys
import tempfile
import functools
import transaction
from collections import OrderedDict

from storm.uri import URI
from twisted.trial import unittest
from twisted.python import filepath
from storm.exceptions import DatabaseModuleError
from storm.twisted.testing import FakeThreadPool
from twisted.internet.defer import inlineCallbacks
from storm.locals import Int, Unicode, Reference, Enum, List

from mamba import Database
from mamba.utils import config
from mamba import Model, ModelManager
from mamba.core import interfaces, GNU_LINUX
from mamba.enterprise.common import NativeEnum
from mamba.application.model import InvalidModelSchema
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
                        "create_table_if_not_exists": %s,
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

        try:
            threadpool = DummyThreadPool()
            self.database = Database(threadpool, True)
            Model.database = self.database

            store = self.database.store()
            store.execute(
                'CREATE TABLE IF NOT EXISTS `dummy` ('
                '    id INTEGER PRIMARY KEY, name TEXT'
                ')'
            )
            store.execute(
                'CREATE TABLE IF NOT EXISTS `dummy_two` ('
                '   dummy_id INTEGER, id INTEGER, name TEXT,'
                '   PRIMARY KEY(dummy_id, id)'
                ')'
            )
            store.commit()
        except DatabaseModuleError as error:
            raise unittest.SkipTest(error)

    def tearDown(self):
        self.flushLoggedErrors()
        self.database.store().reset()
        transaction.manager.free(transaction.get())

    def get_adapter(self, reference=False):

        if reference:
            return DummyModelThree().get_adapter()

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
    def test_model_read_copy(self):
        dummy = yield DummyModel().read(1)
        dummy2 = yield DummyModel().read(1, True)

        self.assertEqual(dummy.name, u'Dummy')
        self.assertEqual(dummy2.name, u'Dummy')
        self.assertNotEqual(dummy, dummy2)

    @inlineCallbacks
    def test_model_update(self):
        dummy = yield DummyModel().read(1)
        dummy.name = u'Fellas'
        dummy.update()

        del(dummy)
        dummy = yield DummyModel().read(1)
        self.assertEqual(dummy.id, 1)
        self.assertEqual(dummy.name, u'Fellas')

    @inlineCallbacks
    def test_model_update_with_read_copy_behaviour(self):
        dummy = yield DummyModel().read(1, True)
        dummy.name = u'Dummy'
        dummy.update()
        del(dummy)

        dummy2 = yield DummyModel().read(1, True)
        self.assertEqual(dummy2.id, 1)
        self.assertEqual(dummy2.name, u'Dummy')

    @inlineCallbacks
    def test_model_update_with_compound_key(self):
        dummy = DummyModelCompound(1, 1, u'Dummy')
        yield dummy.create()
        del(dummy)

        dummy = yield DummyModelCompound().read((1, 1))
        dummy.name = u'Fellas'
        dummy.update()

        del(dummy)
        dummy = yield DummyModelCompound().read((1, 1))
        self.assertEqual(dummy.id, 1)
        self.assertEqual(dummy.dummy_id, 1)
        self.assertEqual(dummy.name, u'Fellas')

    @inlineCallbacks
    def test_model_update_raise_exeption_on_invalid_schema(self):
        dummy = DummyInvalidModel()
        try:
            dummy.name = u'Dummy'
        except:
            # catch storm.exceptions.ClassInfoError
            pass

        try:
            yield dummy.update()
        except InvalidModelSchema:
            pass
        except:
            raise

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

        self.assertTrue('CREATE TABLE IF NOT EXISTS dummy' in script)
        self.assertTrue('PRIMARY KEY(id)' in script)
        self.assertTrue('name varchar(64)' in script)
        self.assertTrue('id serial' in script)

    @common_config(engine='postgres:')
    def test_model_dump_table_with_postgres_and_enum(self):

        dummy = DummyModelEnum()
        script = dummy.dump_table()

        self.assertTrue('mood integer' in script)

    @common_config(engine='postgres:')
    def test_model_dump_table_with_postgres_and_native_enum(self):
        dummy = DummyModelNativeEnum()
        script = dummy.dump_table()

        self.assertTrue("CREATE TYPE enum_mood AS ENUM" in script)
        self.assertTrue("('sad', 'ok', 'happy')" in script)
        self.assertTrue("mood enum_mood" in script)

    @common_config(engine='postgres:')
    def test_model_dump_table_with_postgres_and_array(self):

        dummy = DummyModelArray()
        script = dummy.dump_table()

        self.assertTrue('this_array integer[3][3],' in script)

    @inlineCallbacks
    def test_model_create_table(self):
        dummy = DummyModel()

        yield dummy.create_table()

        store = dummy.database.store()

        self.assertEqual(
            store.execute('''
                SELECT name
                FROM sqlite_master
                WHERE type="table"
                ORDER BY name
            ''').get_one()[0],
            u'dummy'
        )

    @inlineCallbacks
    def test_model_create_and_delete_table(self):
        dummy = DummyModelTwo()

        yield dummy.create_table()
        store = dummy.database.store()

        data = store.execute('''
            SELECT name
            FROM sqlite_master
            WHERE type="table"
            ORDER BY name
        ''').get_all()

        self.assertTrue(len(data) >= 2 and len(data) < 4)
        self.assertEqual(data[1][0], u'dummy_two')

        yield dummy.drop_table()
        data = store.execute('''
            SELECT name
            FROM sqlite_master
            WHERE type="table"
            ORDER BY name
        ''').get_all()

        self.assertTrue(len(data) >= 1 and len(data) < 3)
        self.assertEqual(data[0][0], u'dummy')

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

    @common_config(engine='sqlite:')
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
            adapter.drop_table(), "DROP TABLE IF EXISTS dummy RESTRICT"
        )

    @common_config(engine='postgres:', existance=False)
    def test_postgres_drop_table_no_existance(self):

        adapter = self.get_adapter()
        self.assertEqual(adapter.drop_table(), "DROP TABLE dummy RESTRICT")

    @common_config(engine='postgres:', cascade=True)
    def test_postgres_drop_table_on_cascade(self):

        adapter = self.get_adapter()
        self.assertEqual(
            adapter.drop_table(),
            "DROP TABLE IF EXISTS dummy RESTRICT CASCADE"
        )

    @common_config(engine='postgres:', cascade=False, restrict=False)
    def test_postgres_drop_table_no_restrict(self):

        adapter = self.get_adapter()
        self.assertEqual(
            adapter.drop_table(),
            "DROP TABLE IF EXISTS dummy"
        )

    @common_config(engine='postgres:', cascade=True, restrict=False)
    def test_postgres_drop_table_no_restrict_on_cascade(self):

        adapter = self.get_adapter()
        self.assertEqual(
            adapter.drop_table(),
            "DROP TABLE IF EXISTS dummy CASCADE"
        )

    @common_config(engine='mysql:')
    def test_mysql_reference_generates_foreign_keys(self):

        adapter = self.get_adapter(reference=True)
        script = adapter.create_table()

        self.assertTrue('INDEX `dummy_two_ind` (`remote_id`)' in script)
        self.assertTrue(
            'FOREIGN KEY (`remote_id`) REFERENCES `dummy_two`(`id`)' in script
        )
        self.assertTrue('ON UPDATE RESTRICT ON DELETE RESTRICT' in script)

    @common_config(engine='mysql:')
    def test_mysql_reference_in_cascade(self):

        DummyModelThree.__on_delete__ = 'CASCADE'
        DummyModelThree.__on_update__ = 'CASCADE'

        adapter = self.get_adapter(reference=True)
        script = adapter.create_table()

        self.assertTrue('ON UPDATE CASCADE ON DELETE CASCADE' in script)
        del DummyModelThree.__on_delete__
        del DummyModelThree.__on_update__

    @common_config(engine='postgres:')
    def test_postgres_reference_generates_foreign_keys(self):

        adapter = self.get_adapter(reference=True)
        script = adapter.parse_references()

        self.assertTrue(
            'CONSTRAINT dummy_two_ind FOREIGN KEY (remote_id)' in script
        )
        self.assertTrue(
            'REFERENCES dummy_two(id) ON UPDATE RESTRICT ON DELETE RESTRICT'
            in script
        )

    @common_config(engine='postgres:')
    def test_postgres_reference_in_cascade(self):

        DummyModelThree.__on_delete__ = 'CASCADE'
        DummyModelThree.__on_update__ = 'CASCADE'

        adapter = self.get_adapter(reference=True)
        script = adapter.parse_references()

        self.assertTrue('ON UPDATE CASCADE ON DELETE CASCADE' in script)
        del DummyModelThree.__on_delete__
        del DummyModelThree.__on_update__


class ModelManagerTest(unittest.TestCase):
    """Tests for mamba.application.model.ModelManager
    """

    def setUp(self):
        self.mgr = ModelManager()
        if GNU_LINUX:
            self.addCleanup(self.mgr.notifier.loseConnection)
        try:
            threadpool = DummyThreadPool()
            self.database = Database(threadpool, True)
            Model.database = self.database

            store = self.database.store()
            store.execute(
                'CREATE TABLE IF NOT EXISTS `dummy` ('
                '    id INTEGER PRIMARY KEY, name TEXT'
                ')'
            )
            store.commit()
        except DatabaseModuleError as error:
            raise unittest.SkipTest(error)

    def tearDown(self):
        self.flushLoggedErrors()
        self.database.store().reset()
        transaction.manager.free(transaction.get())

    def load_manager(self):
        sys.path.append('../mamba/test/dummy_app')
        self.mgr.load('../mamba/test/dummy_app/application/model/dummy.py')

    def test_constructor_overwrites_module_store(self):
        mgr = ModelManager('overwritten/store')
        if GNU_LINUX:
            self.addCleanup(mgr.notifier.loseConnection)
        self.assertEqual(mgr._module_store, 'overwritten/store')

    def test_inotifier_provided_by_controller_manager(self):
        if not GNU_LINUX:
            raise unittest.SkipTest('File monitoring only available on Linux')
        self.assertTrue(interfaces.INotifier.providedBy(self.mgr))

    def test_get_models_is_ordered_dict(self):
        self.assertIsInstance(self.mgr.get_models(), OrderedDict)

    def test_get_models_is_empty(self):
        self.assertNot(self.mgr.get_models())

    def test_is_valid_file_works_on_valid(self):
        import os
        currdir = os.getcwd()
        os.chdir('../mamba/test/dummy_app')
        self.assertTrue(self.mgr.is_valid_file('dummy.py'))
        os.chdir(currdir)

    def test_is_valid_file_works_on_invalid(self):
        self.assertFalse(self.mgr.is_valid_file('./test.log'))

    def test_is_valid_file_works_with_filepath(self):
        import os
        currdir = os.getcwd()
        os.chdir('../mamba/test/dummy_app')
        self.assertTrue(self.mgr.is_valid_file(filepath.FilePath('dummy.py')))
        os.chdir(currdir)

    def test_load_modules_works(self):
        self.load_manager()
        self.assertTrue(self.mgr.length() != 0)

    def test_lookup(self):
        unknown = self.mgr.lookup('unknown')
        self.assertEqual(unknown, {})

        self.load_manager()
        dummy = self.mgr.lookup('dummy').get('object')
        self.assertTrue(dummy.__storm_table__ == 'dummy')
        self.assertTrue(dummy.loaded)

    def test_reload(self):
        self.load_manager()
        dummy = self.mgr.lookup('dummy').get('object')

        self.mgr.reload('dummy')
        dummy2 = self.mgr.lookup('dummy').get('object')

        self.assertNotEqual(dummy, dummy2)


class DummyInvalidModel(Model):
    """Dummy Model without primary key for testing purposes
    """

    __storm_table__ = 'dummy'
    id = Int(auto_increment=True, unigned=True)
    name = Unicode(size=64, allow_none=False)

    def __init__(self, name=None):
        super(DummyInvalidModel, self).__init__()

        if name is not None:
            self.name = unicode(name)


class DummyModel(Model):
    """Dummy Model for testing purposes"""

    __storm_table__ = 'dummy'
    id = Int(primary=True, auto_increment=True, unsigned=True)
    name = Unicode(size=64, allow_none=False)

    def __init__(self, name=None):
        super(DummyModel, self).__init__()

        if name is not None:
            self.name = unicode(name)


class DummyModelTwo(Model):
    """Dummy Model for testing purposes"""

    __storm_table__ = 'dummy_two'
    id = Int(primary=True, auto_increment=True, unsigned=True)
    name = Unicode(size=64, allow_none=False)

    def __init__(self, name=None):
        super(DummyModelTwo, self).__init__()

        if name is not None:
            self.name = unicode(name)


class DummyModelCompound(Model):
    """Dummy Model for testing purposes"""

    __storm_table__ = 'dummy_two'
    __storm_primary__ = 'id', 'dummy_id'
    id = Int(unsigned=True)
    dummy_id = Int(unsigned=True)

    def __init__(self, id=None, dummy_id=None, name=None):
        super(DummyModelCompound, self).__init__()

        self.id = id
        self.dummy_id = dummy_id
        self.name = name


class DummyModelThree(Model):
    """Dummy Model for testing purposes"""

    __storm_table__ = 'dummy_three'
    id = Int(primary=True)
    remote_id = Int()
    dummy_two = Reference(remote_id, DummyModelTwo.id)


class DummyModelEnum(Model):
    """Dummy Model for testing purposes"""

    __storm_table__ = 'dummy_enum'
    id = Int(primary=True)
    mood = Enum(map={'sad': 1, 'ok': 2, 'happy': 3})


class DummyModelNativeEnum(Model):
    """Dummy Model for testing purposes"""

    __storm_table__ = 'dummy_enum'
    id = Int(primary=True)
    mood = NativeEnum(map={'sad': 1, 'ok': 2, 'happy': 3})


class DummyModelArray(Model):
    """Dummy Model for testing purposes"""

    __storm_table__ = 'dummy_array'
    id = Int(primary=True)
    this_array = List(array='integer[3][3]')


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
