
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
Tests for mamba.application.model
"""

import sys
import datetime
import tempfile
import functools
import transaction
from collections import OrderedDict

from storm.uri import URI
from twisted.trial import unittest
from twisted.python import filepath
from storm.exceptions import DatabaseModuleError, NoneError
from storm.twisted.testing import FakeThreadPool
from twisted.internet.defer import inlineCallbacks, Deferred
from storm.locals import (
    Int, Unicode, Reference, Enum, List, Bool, DateTime, Decimal
)

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

    def get_adapter(self, reference=False, compound=False):

        if reference and compound:
            return DummyModelFive().get_adapter()
        elif reference:
            return DummyModelThree().get_adapter()

        return DummyModel().get_adapter()

    def insert_dummy(self, name='Dummy'):

        store = self.database.store()
        store.execute('INSERT INTO dummy (name) VALUES (\'{}\')'.format(name))
        store.commit()

    def truncate_dummy(self):

        store = self.database.store()
        store.execute('DELETE FROM dummy')
        store.commit()

    @inlineCallbacks
    def test_model_create(self):
        dummy = DummyModel('Dummy')
        yield dummy.create()

        self.assertEqual(dummy.id, 1)

    def test_model_synchronous_create(self):
        dummy = DummyModel('Dummy')
        dummy.create(async=False)

        self.assertEqual(dummy.id, 1)

    @inlineCallbacks
    def test_model_read(self):
        self.insert_dummy()
        dummy = yield DummyModel().read(1)
        self.assertEqual(dummy.id, 1)
        self.assertEqual(dummy.name, u'Dummy')
        self.truncate_dummy()

    @inlineCallbacks
    def test_model_read_as_class_method(self):
        self.insert_dummy()
        dummy = yield DummyModel.read(1)
        self.assertEqual(dummy.id, 1)
        self.assertEqual(dummy.name, u'Dummy')
        self.truncate_dummy()

    def test_model_read_raises_type_error_on_wrong_instantiation(self):

        class NonInstantiableByRead(Model):

            def __init__(self, one):
                pass

        self.assertRaises(
            TypeError, NonInstantiableByRead.read, 1, async=False)

    def test_model_read_non_raises_type_error_when_defaults_are_defined(self):

        class InstantiableByRead(Model):

            __storm_table__ = 'dummy'

            id = Int(primary=True)

            def __init__(self, one=1):
                pass

        self.assertEqual(None, InstantiableByRead.read(1, async=False))

    def test_model_synchronous_read(self):
        self.insert_dummy()
        dummy = DummyModel().read(1, async=False)
        self.assertEqual(dummy.id, 1)
        self.assertEqual(dummy.name, u'Dummy')
        self.truncate_dummy()

    def test_model_synchronous_read_as_class_method(self):
        self.insert_dummy()
        dummy = DummyModel.read(1, async=False)
        self.assertEqual(dummy.id, 1)
        self.assertEqual(dummy.name, u'Dummy')
        self.truncate_dummy()

    @inlineCallbacks
    def test_model_read_copy(self):
        self.insert_dummy()
        dummy = yield DummyModel().read(1)
        dummy2 = yield DummyModel().read(1, True)

        self.assertEqual(dummy.name, u'Dummy')
        self.assertEqual(dummy2.name, u'Dummy')
        self.assertNotEqual(dummy, dummy2)
        self.truncate_dummy()

    @inlineCallbacks
    def test_model_read_copy_as_class_method(self):
        self.insert_dummy()
        dummy = yield DummyModel.read(1)
        dummy2 = yield DummyModel.read(1, True)

        self.assertEqual(dummy.name, u'Dummy')
        self.assertEqual(dummy2.name, u'Dummy')
        self.assertNotEqual(dummy, dummy2)
        self.truncate_dummy()

    def test_model_read_synchronous_copy(self):
        self.insert_dummy()
        dummy = DummyModel().read(1, async=False)
        dummy2 = DummyModel().read(1, True, async=False)

        self.assertEqual(dummy.name, u'Dummy')
        self.assertEqual(dummy2.name, u'Dummy')
        self.assertNotEqual(dummy, dummy2)
        self.truncate_dummy()

    def test_model_read_synchronous_copy_as_class_method(self):
        self.insert_dummy()
        dummy = DummyModel.read(1, async=False)
        dummy2 = DummyModel.read(1, True, async=False)

        self.assertEqual(dummy.name, u'Dummy')
        self.assertEqual(dummy2.name, u'Dummy')
        self.assertNotEqual(dummy, dummy2)
        self.truncate_dummy()

    @inlineCallbacks
    def test_model_update(self):
        self.insert_dummy()
        dummy = yield DummyModel().read(1)
        dummy.name = u'Fellas'
        dummy.update()

        del(dummy)
        dummy = yield DummyModel().read(1)
        self.assertEqual(dummy.id, 1)
        self.assertEqual(dummy.name, u'Fellas')
        self.truncate_dummy()

    def test_model_synchronous_update(self):
        self.insert_dummy()
        dummy = DummyModel().read(1, async=False)
        dummy.name = u'Fellas'
        dummy.update()

        del(dummy)
        dummy = DummyModel().read(1, async=False)
        self.assertEqual(dummy.id, 1)
        self.assertEqual(dummy.name, u'Fellas')
        self.truncate_dummy()

    @inlineCallbacks
    def test_model_update_with_read_copy_behaviour(self):
        self.insert_dummy()
        dummy = yield DummyModel().read(1, True)
        dummy.name = u'Dummy'
        dummy.update()
        del(dummy)

        dummy2 = yield DummyModel().read(1, True)
        self.assertEqual(dummy2.id, 1)
        self.assertEqual(dummy2.name, u'Dummy')
        self.truncate_dummy()

    @inlineCallbacks
    def test_model_update_with_read_as_class_method_copy_behaviour(self):
        self.insert_dummy()
        dummy = yield DummyModel.read(1, True)
        dummy.name = u'Dummy'
        dummy.update()
        del(dummy)

        dummy2 = yield DummyModel.read(1, True)
        self.assertEqual(dummy2.id, 1)
        self.assertEqual(dummy2.name, u'Dummy')
        self.truncate_dummy()

    def test_model_update_with_read_copy_synchornous_behaviour(self):
        self.insert_dummy()
        dummy = DummyModel().read(1, True, async=False)
        dummy.name = u'Dummy'
        dummy.update()
        del(dummy)

        dummy2 = DummyModel().read(1, True, async=False)
        self.assertEqual(dummy2.id, 1)
        self.assertEqual(dummy2.name, u'Dummy')
        self.truncate_dummy()

    def test_model_update_with_read_as_class_method_copy_synchornous_behaviour(
            self):
        self.insert_dummy()
        dummy = DummyModel.read(1, True, async=False)
        dummy.name = u'Dummy'
        dummy.update()
        del(dummy)

        dummy2 = DummyModel.read(1, True, async=False)
        self.assertEqual(dummy2.id, 1)
        self.assertEqual(dummy2.name, u'Dummy')
        self.truncate_dummy()

    @inlineCallbacks
    def test_model_update_with_compound_key(self):
        dummy = DummyModelCompound(1, 1, u'Dummy')
        yield dummy.create()
        del(dummy)

        dummy = yield DummyModelCompound().read((1, 1))
        dummy.name = u'Fellas'
        yield dummy.update()

        del(dummy)
        dummy = yield DummyModelCompound().read((1, 1))
        self.assertEqual(dummy.id, 1)
        self.assertEqual(dummy.dummy_id, 1)
        self.assertEqual(dummy.name, u'Fellas')
        self.truncate_dummy()

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

    def test_model_update_synchronous_raise_exeption_on_invalid_schema(self):
        dummy = DummyInvalidModel()
        try:
            dummy.name = u'Dummy'
        except:
            # catch storm.exceptions.ClassInfoError
            pass

        try:
            dummy.update(async=False)
        except InvalidModelSchema:
            pass
        except:
            raise

    @inlineCallbacks
    def test_model_delete(self):
        dummy = yield DummyModel().read(1)
        yield dummy.delete()

        store = self.database.store()
        self.assertTrue(store.find(DummyModel).count() == 0)

    def test_model_synchronous_delete(self):
        dummy = DummyModel().read(1, async=False)
        dummy.delete()

        store = self.database.store()
        self.assertTrue(store.find(DummyModel).count() == 0)

    @inlineCallbacks
    def test_model_find(self):
        self.insert_dummy()
        result = yield DummyModel().find(DummyModel.name == u'Dummy')
        dummy = result.one()
        self.assertEqual(dummy.id, 1)
        self.assertEqual(dummy.name, u'Dummy')
        self.truncate_dummy()

    @inlineCallbacks
    def test_model_find_no_instance(self):
        self.insert_dummy()
        result = yield DummyModel.find(name=u'Dummy')
        dummy = result.one()
        self.assertEqual(dummy.id, 1)
        self.assertEqual(dummy.name, u'Dummy')
        self.truncate_dummy()

    def test_model_synchornous_find(self):
        self.insert_dummy()
        dummy = DummyModel().find(name=u'Dummy', async=False).one()
        self.assertEqual(dummy.id, 1)
        self.assertEqual(dummy.name, u'Dummy')
        self.truncate_dummy()

    def test_model_synchornous_find_no_instance(self):
        self.insert_dummy()
        dummy = DummyModel.find(name=u'Dummy', async=False).one()
        self.assertEqual(dummy.id, 1)
        self.assertEqual(dummy.name, u'Dummy')
        self.truncate_dummy()

    @inlineCallbacks
    def test_model_all(self):
        self.insert_dummy()
        self.insert_dummy('Dummy2')
        dummy = yield DummyModel().all()
        self.assertEqual(dummy.count(), 2)
        self.assertEqual(dummy[0].id, 1)
        self.assertEqual(dummy[0].name, u'Dummy')
        self.truncate_dummy()

    @inlineCallbacks
    def test_model_all_no_instance(self):
        self.insert_dummy()
        self.insert_dummy('Dummy2')
        dummy = yield DummyModel.all()
        self.assertEqual(dummy.count(), 2)
        self.assertEqual(dummy[0].id, 1)
        self.assertEqual(dummy[0].name, u'Dummy')
        self.truncate_dummy()

    def test_model_synchronous_all(self):
        self.insert_dummy()
        self.insert_dummy('Dummy2')
        dummy = DummyModel().all(async=False)
        self.assertEqual(dummy.count(), 2)
        self.assertEqual(dummy[0].id, 1)
        self.assertEqual(dummy[0].name, u'Dummy')
        self.truncate_dummy()

    def test_model_synchronous_all_no_instance(self):
        self.insert_dummy()
        self.insert_dummy('Dummy2')
        dummy = DummyModel.all(async=False)
        self.assertEqual(dummy.count(), 2)
        self.assertEqual(dummy[0].id, 1)
        self.assertEqual(dummy[0].name, u'Dummy')
        self.truncate_dummy()

    @inlineCallbacks
    def test_model_all_order_by(self):
        self.insert_dummy()
        self.insert_dummy('OrderTest')
        dummy = yield DummyModel().all(order_by=DummyModel.name)
        self.assertEqual(dummy.count(), 2)
        self.assertEqual(dummy[0].id, 1)
        self.assertEqual(dummy[0].name, u'Dummy')
        dummy = yield DummyModel().all(order_by=DummyModel.name, desc=True)
        self.assertEqual(dummy.count(), 2)
        self.assertEqual(dummy[0].id, 2)
        self.assertEqual(dummy[0].name, u'OrderTest')
        self.truncate_dummy()

    def test_model_global_behaviour_sync(self):
        self.insert_dummy()
        DummyModel.__mamba_async__ = False
        dummy = DummyModel().read(1)
        self.assertTrue(isinstance(dummy, DummyModel))

    def test_model_global_behaviour_async(self):
        self.insert_dummy()
        DummyModel.__mamba_async__ = True
        dummy = DummyModel().read(1)
        self.assertTrue(isinstance(dummy, Deferred))

    @inlineCallbacks
    def test_model_all_order_by_no_instance(self):
        self.insert_dummy()
        self.insert_dummy('OrderTest')
        dummy = yield DummyModel.all(order_by=DummyModel.name)
        self.assertEqual(dummy.count(), 2)
        self.assertEqual(dummy[0].id, 1)
        self.assertEqual(dummy[0].name, u'Dummy')
        dummy = yield DummyModel.all(order_by=DummyModel.name, desc=True)
        self.assertEqual(dummy.count(), 2)
        self.assertEqual(dummy[0].id, 2)
        self.assertEqual(dummy[0].name, u'OrderTest')
        self.truncate_dummy()

    def test_model_synchronous_all_order_by(self):
        self.insert_dummy()
        self.insert_dummy('OrderTest')
        dummy = DummyModel().all(order_by=DummyModel.name, async=False)
        self.assertEqual(dummy.count(), 2)
        self.assertEqual(dummy[0].id, 1)
        self.assertEqual(dummy[0].name, u'Dummy')
        dummy = DummyModel().all(
            order_by=DummyModel.name, desc=True, async=False)
        self.assertEqual(dummy.count(), 2)
        self.assertEqual(dummy[0].id, 2)
        self.assertEqual(dummy[0].name, u'OrderTest')
        self.truncate_dummy()

    def test_model_synchronous_all_order_by_no_instance(self):
        self.insert_dummy()
        self.insert_dummy('OrderTest')
        dummy = DummyModel.all(order_by=DummyModel.name, async=False)
        self.assertEqual(dummy.count(), 2)
        self.assertEqual(dummy[0].id, 1)
        self.assertEqual(dummy[0].name, u'Dummy')
        dummy = DummyModel.all(
            order_by=DummyModel.name, desc=True, async=False)
        self.assertEqual(dummy.count(), 2)
        self.assertEqual(dummy[0].id, 2)
        self.assertEqual(dummy[0].name, u'OrderTest')
        self.truncate_dummy()

    def test_model_dump_table(self):
        dummy = DummyModel()
        script = dummy.dump_table()

        self.assertTrue('CREATE TABLE IF NOT EXISTS dummy' in script)
        self.assertTrue('PRIMARY KEY(id)' in script)
        self.assertTrue('name varchar' in script)
        self.assertTrue('id integer' in script)

    def test_model_dump_ordered_fields(self):
        dummy = DummyModelDecimal()
        script = dummy.dump_table()
        split_script = script.split('\n')

        self.assertTrue('id integer' in split_script[1])
        self.assertTrue('money text' in split_script[2])
        self.assertTrue('money2 text' in split_script[3])
        self.assertTrue('money3 text' in split_script[4])

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

    @common_config(engine='mysql:')
    def test_model_dump_table_with_mysql_primary_key_is_first_field(self):

        dummy = DummyModel()
        script = dummy.dump_table()

        self.assertTrue(
            '`id` int UNSIGNED AUTO_INCREMENT' in script.split(',')[0]
        )

    @common_config(engine='mysql:')
    def test_model_dump_table_with_mysql_compound_pk_are_firsts_field(self):

        dummy = DummyModelSix()
        script = dummy.dump_table()

        self.assertTrue('`id` int' in script.split(',')[0])
        self.assertTrue('`second_id` int' in script.split(',')[1])

    @common_config(engine='mysql:')
    def test_model_dump_table_with_mysql_unique_field(self):

        dummy = DummyModelSeven()
        script = dummy.dump_table()

        self.assertTrue('`id` int' in script)
        self.assertTrue('`second_id` int' in script)

        self.assertTrue('UNIQUE `second_id_uni` (`second_id`)' in script)

    @common_config(engine='mysql:')
    def test_model_dump_table_with_mysql_compound_unique_field(self):

        dummy = DummyModelEight()
        script = dummy.dump_table()

        self.assertTrue('`id` int' in script)
        self.assertTrue('`second_id` int' in script)

        self.assertTrue((
            'UNIQUE `second_id_third_id_uni` '
            '(`second_id`, `third_id`)') in script
        )

    @common_config(engine='mysql:')
    def test_model_dump_table_with_mysql_compound_index_field(self):

        dummy = DummyModelEight()
        script = dummy.dump_table()

        self.assertTrue('`id` int' in script)
        self.assertTrue('`second_id` int' in script)

        self.assertTrue((
            'INDEX `second_id_fourth_id_ind` '
            '(`second_id`, `fourth_id`)') in script
        )

    @common_config(engine='mysql:')
    def test_model_dump_table_with_mysql_index_field(self):

        dummy = DummyModelSeven()
        script = dummy.dump_table()

        self.assertTrue('`id` int' in script)
        self.assertTrue('`second_id` int' in script)

        self.assertTrue('INDEX `third_id_ind` (`third_id`)' in script)

    @common_config(engine='mysql:')
    def test_model_dump_table_with_mysql_unique_has_no_index_field(self):

        dummy = DummyModelSeven()
        script = dummy.dump_table()

        self.assertTrue('`id` int' in script)
        self.assertTrue('`second_id` int' in script)

        self.assertTrue('UNIQUE `fourth_id_uni` (`fourth_id`)' in script)

        self.assertTrue('INDEX `fourth_id_ind` (`fourth_id`)' not in script)

    @common_config(engine='mysql:')
    def test_model_dump_table_with_mysql_and_native_enum(self):
        dummy = DummyModelNativeEnum()
        script = dummy.dump_table()
        self.assertTrue(
            'sad' in script and 'ok' in script and 'happy' in script
        )

    @common_config(engine='mysql:')
    def test_model_dump_table_with_mysql_and_bool_with_default_value(self):

        dummy = DummyModelBool()
        script = dummy.dump_table()
        self.assertTrue('  `test` tinyint default 1' in script)

    @common_config(engine='mysql:')
    def test_model_dump_table_with_mysql_and_default_value_none(self):

        dummy = DummyModelNone()
        script = dummy.dump_table()
        self.assertTrue('  `name` varchar(64) default NULL,' in script)

    @common_config(engine='mysql:')
    def test_model_dump_table_with_mysql_and_datetime_default(self):

        dummy = DummyModelDatetime()
        script = dummy.dump_table()
        self.assertTrue(
            "  `time` datetime default '2013-01-01 00:00:00'," in script)

    @common_config(engine='mysql:')
    def test_model_dump_table_with_mysql_and_decimal_with_float(self):

        dummy = DummyModelDecimal()
        script = dummy.dump_table()
        self.assertTrue('  `money` decimal(10,2),' in script)

    @common_config(engine='mysql:')
    def test_model_dump_table_with_mysql_and_decimal_with_tuple(self):

        dummy = DummyModelDecimal()
        script = dummy.dump_table()
        self.assertTrue('  `money2` decimal(10,2),' in script)

    @common_config(engine='mysql:')
    def test_model_dump_table_with_mysql_and_decimal_with_list(self):

        dummy = DummyModelDecimal()
        script = dummy.dump_table()
        self.assertTrue('  `money3` decimal(10,2),' in script)

    @common_config(engine='mysql:')
    def test_model_dump_table_with_mysql_and_decimal_with_string(self):

        dummy = DummyModelDecimal()
        script = dummy.dump_table()
        self.assertTrue('  `money4` decimal(10,2),' in script)

    @common_config(engine='postgres:')
    def test_model_dump_table_with_postgres(self):

        dummy = DummyModel()
        script = dummy.dump_table()

        self.assertTrue('CREATE TABLE IF NOT EXISTS dummy' in script)
        self.assertTrue('PRIMARY KEY(id)' in script)
        self.assertTrue('name varchar(64)' in script)
        self.assertTrue('id serial' in script)

    @common_config(engine='postgres:')
    def test_model_dump_table_with_postgres_unique_field(self):

        dummy = DummyModelSeven()
        script = dummy.dump_table()

        self.assertTrue('id int' in script)
        self.assertTrue('second_id int UNIQUE' in script)
        self.assertTrue('fourth_id int UNIQUE' in script)

    @common_config(engine='postgres:')
    def test_model_dump_table_with_postgres_index_field(self):

        dummy = DummyModelSeven()
        script = dummy.dump_table() + dummy.dump_indexes()

        self.assertTrue('id int' in script)
        self.assertTrue('second_id int UNIQUE' in script)
        self.assertTrue('fourth_id int UNIQUE' in script)

        self.assertTrue(
            'CREATE INDEX third_id_ind ON dummy_seven (third_id)' in script
        )

    @common_config(engine='postgres:')
    def test_model_dump_table_with_postgres_compound_index_field(self):

        dummy = DummyModelEight()
        script = dummy.dump_table() + dummy.dump_indexes()

        self.assertTrue('id int' in script)
        self.assertTrue('second_id int,' in script)
        self.assertTrue('fourth_id int,' in script)

        self.assertTrue((
            'CREATE INDEX second_id_fourth_id_ind ON'
            ' dummy_eight (second_id, fourth_id)') in script
        )

    @common_config(engine='postgres:')
    def test_model_dump_table_with_postgres_compound_unique_field(self):

        dummy = DummyModelEight()
        script = dummy.dump_table()

        self.assertTrue('id int' in script)
        self.assertTrue('second_id int,' in script)
        self.assertTrue('fourth_id int,' in script)
        self.assertTrue('UNIQUE (second_id, third_id)' in script)

    @common_config(engine='postgres:')
    def test_model_dump_table_with_postgres_primary_key_is_first_field(self):

        dummy = DummyModel()
        script = dummy.dump_table()

        self.assertTrue(
            'id serial' in script.split(',')[0]
        )

    @common_config(engine='postgres:')
    def test_model_dump_table_with_postgres_compound_pk_are_firsts_field(self):

        dummy = DummyModelSix()
        script = dummy.dump_table()

        self.assertTrue('id int' in script.split(',')[0])
        self.assertTrue('second_id int' in script.split(',')[1])

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
        self.assertTrue(
            'sad' in script and 'ok' in script and 'happy' in script
        )
        self.assertTrue("mood enum_mood" in script)

    @common_config(engine='postgres:')
    def test_model_dump_table_with_postgres_and_array(self):

        dummy = DummyModelArray()
        script = dummy.dump_table()

        self.assertTrue('this_array integer[3][3],' in script)

    @common_config(engine='postgres:')
    def test_model_dump_table_with_postgres_and_bool_with_default_value(self):

        dummy = DummyModelBool()
        script = dummy.dump_table()
        self.assertTrue('  test bool default TRUE' in script)

    @common_config(engine='postgres:')
    def test_model_dump_table_with_postgres_and_default_value_none(self):

        dummy = DummyModelNone()
        script = dummy.dump_table()
        self.assertTrue('  name varchar(64) default NULL,' in script)

    @common_config(engine='postgres:')
    def test_model_dump_table_with_postgres_and_datetime_default(self):

        dummy = DummyModelDatetime()
        script = dummy.dump_table()
        self.assertTrue(
            "  time timestamp default '2013-01-01 00:00:00'," in script)

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
        config.Database('clean')
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
        config.Database('clean')
        dummy = DummyModel()
        self.assertEqual(dummy.get_uri().scheme, URI('sqlite:').scheme)

    def test_get_adapter(self):
        dummy = DummyModel()
        adapter = dummy.get_adapter()
        self.assertTrue(interfaces.IMambaSQL.providedBy(adapter))

    def test_model_allow_none_false_raises_exception(self):
        dummy = DummyModel()
        self.assertRaises(NoneError, dummy.create, async=False)

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

    @common_config(engine='sqlite:')
    def test_model_dump_table_with_sqlite_primary_key_is_first_field(self):

        dummy = DummyModel()
        script = dummy.dump_table()

        self.assertTrue('id integer' in script.split(',')[0])

    @common_config(engine='sqlite:')
    def test_model_dump_table_with_sqlite_unique_field(self):

        dummy = DummyModelSeven()
        script = dummy.dump_table()

        self.assertTrue('id integer,' in script)
        self.assertTrue('second_id integer UNIQUE,' in script)
        self.assertTrue('fourth_id integer UNIQUE,' in script)

    @common_config(engine='sqlite:')
    def test_model_dump_table_with_sqlite_index_field(self):

        dummy = DummyModelSeven()
        script = dummy.dump_table() + dummy.dump_indexes()

        self.assertTrue('id integer' in script)
        self.assertTrue('second_id integer UNIQUE' in script)
        self.assertTrue('fourth_id integer UNIQUE' in script)

        self.assertTrue(
            'CREATE INDEX third_id_ind ON dummy_seven (third_id)' in script
        )

    @common_config(engine='sqlite:')
    def test_model_dump_table_with_sqlite_compound_index_field(self):

        dummy = DummyModelEight()
        script = dummy.dump_table() + dummy.dump_indexes()

        self.assertTrue('id integer' in script)
        self.assertTrue('second_id integer,' in script)
        self.assertTrue('fourth_id integer,' in script)

        self.assertTrue((
            'CREATE INDEX second_id_fourth_id_ind ON'
            ' dummy_eight (second_id, fourth_id)') in script
        )

    @common_config(engine='sqlite:')
    def test_model_dump_table_with_sqlite_compound_unique_field(self):

        dummy = DummyModelEight()
        script = dummy.dump_table()

        self.assertTrue('id integer,' in script)
        self.assertTrue('second_id integer,' in script)
        self.assertTrue('fourth_id integer,' in script)
        self.assertTrue('UNIQUE (second_id, third_id)' in script)

    @common_config(engine='sqlite:')
    def test_model_dump_table_with_sqlite_compound_pk_are_firsts_field(self):

        dummy = DummyModelSix()
        script = dummy.dump_table()

        self.assertTrue('id integer' in script.split(',')[0])
        self.assertTrue('second_id integer' in script.split(',')[1])

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

    @common_config(engine='sqlite:')
    def test_sqlite_reference_generates_foreign_keys(self):

        adapter = self.get_adapter(reference=True)
        script = adapter.create_table()

        self.assertTrue(
            'FOREIGN KEY(remote_id) REFERENCES dummy_two(id)' in script)
        self.assertTrue('ON DELETE NO ACTION ON UPDATE NO ACTION' in script)

    @common_config(engine='sqlite:')
    def test_sqlite_reference_generates_compound_foreign_keys(self):

        adapter = self.get_adapter(reference=True, compound=True)
        script = adapter.create_table()
        self.assertTrue(
            'FOREIGN KEY(remote_id, remote_second_id) REFERENCES '
            'dummy_four(id, second_id) ON DELETE NO ACTION ON UPDATE NO ACTION'
            in script
        )

    @common_config(engine='sqlite:')
    def test_sqlite_rerefence_in_restrict(self):

        DummyModelThree.__on_delete__ = 'RESTRICT'
        DummyModelThree.__on_update__ = 'RESTRICT'

        adapter = self.get_adapter(reference=True)
        script = adapter.create_table()

        self.assertTrue('ON DELETE RESTRICT ON UPDATE RESTRICT' in script)

    @common_config(engine='sqlite:')
    def test_sqlite_rerefence_in_cascade(self):

        DummyModelThree.__on_delete__ = 'CASCADE'
        DummyModelThree.__on_update__ = 'CASCADE'

        adapter = self.get_adapter(reference=True)
        script = adapter.create_table()

        self.assertTrue('ON DELETE CASCADE ON UPDATE CASCADE' in script)

    @common_config(engine='sqlite:')
    def test_sqlite_rerefence_set_null(self):

        DummyModelThree.__on_delete__ = 'SET NULL'
        DummyModelThree.__on_update__ = 'SET NULL'

        adapter = self.get_adapter(reference=True)
        script = adapter.create_table()

        self.assertTrue('ON DELETE SET NULL ON UPDATE SET NULL' in script)

    @common_config(engine='sqlite:')
    def test_sqlite_rerefence_set_default(self):

        DummyModelThree.__on_delete__ = 'SET DEFAULT'
        DummyModelThree.__on_update__ = 'SET DEFAULT'

        adapter = self.get_adapter(reference=True)
        script = adapter.create_table()

        self.assertTrue(
            'ON DELETE SET DEFAULT ON UPDATE SET DEFAULT' in script)

    @common_config(engine='mysql:')
    def test_mysql_reference_generates_foreign_keys(self):

        adapter = self.get_adapter(reference=True)
        script = adapter.create_table()

        self.assertTrue('INDEX `dummy_two_fk_ind` (`remote_id`)' in script)
        self.assertTrue(
            'FOREIGN KEY (`remote_id`) REFERENCES `dummy_two`(`id`)' in script
        )
        self.assertTrue('ON UPDATE RESTRICT ON DELETE RESTRICT' in script)

    @common_config(engine='mysql:')
    def test_mysql_reference_generates_compound_foreign_keys(self):

        adapter = self.get_adapter(reference=True, compound=True)
        script = adapter.create_table()

        self.assertTrue(
            ('INDEX `dummy_four_fk_ind` '
                '(`remote_id`, `remote_second_id`)') in script
        )
        self.assertTrue(
            ('FOREIGN KEY (`remote_id`, `remote_second_id`) REFERENCES'
                ' `dummy_four`(`id`, `second_id`)') in script
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
    def test_postgres_reference_generates_compound_foreign_keys(self):

        adapter = self.get_adapter(reference=True, compound=True)
        script = adapter.parse_references()

        self.assertTrue(
            ('CONSTRAINT dummy_four_ind FOREIGN KEY '
                '(remote_id, remote_second_id)') in script
        )
        self.assertTrue(
            ('REFERENCES dummy_four(id, second_id) '
                'ON UPDATE RESTRICT ON DELETE RESTRICT') in script
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
        self.flushLoggedErrors()
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

    def test_length(self):
        self.assertEqual(self.mgr.length(), 0)
        self.load_manager()
        self.assertEqual(self.mgr.length(), 1)


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


class DummyModelBool(Model):
    """Dummy Model for testing purposes"""

    __storm_table__ = 'dummy_bool'
    id = Int(primary=True, auto_increment=True, unsigned=True)
    test = Bool(default=True)


class DummyModelNone(Model):
    """Dummy model for testing purposes"""

    __storm_table__ = 'dummy_none'
    id = Int(primary=True, auto_increment=True, unsigned=True)
    name = Unicode(size=64, default=None)


class DummyModelDatetime(Model):
    """Dummy model for testing purposes"""

    __storm_table__ = 'dummy_datetime'
    id = Int(primary=True, auto_increment=True, unsigned=True)
    time = DateTime(default=datetime.datetime(2013, 1, 1, 0, 0))


class DummyModelDecimal(Model):
    """Dummy model for testing purposes"""

    __storm_table__ = 'dummy_decimal'
    id = Int(primary=True, auto_increment=True, unsigned=True)
    money = Decimal(size=10.2)
    money2 = Decimal(size=(10, 2))
    money3 = Decimal(size=[10, 2])
    money4 = Decimal(size='10,2')


class DummyModelCompound(Model):
    """Dummy Model for testing purposes"""

    __storm_table__ = 'dummy_two'
    __storm_primary__ = 'id', 'dummy_id'
    id = Int(unsigned=True)
    dummy_id = Int(unsigned=True)
    name = Unicode()

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


class DummyModelFour(Model):
    """Dummy Model for testing purposes"""

    __storm_table__ = 'dummy_four'
    __storm_primary__ = 'id', 'second_id'
    id = Int()
    second_id = Int()


class DummyModelFive(Model):
    """Dummy Model for testing purposes"""

    __storm_table__ = 'dummy_five'
    id = Int(primary=True)
    remote_id = Int()
    remote_second_id = Int()
    dummy_four = Reference(
        (remote_id, remote_second_id),
        (DummyModelFour.id, DummyModelFour.second_id)
    )


class DummyModelSix(Model):
    """Dummy Model for testing purposes"""

    __storm_table__ = 'dummy_six'
    __storm_primary__ = 'id', 'second_id'
    id = Int()
    second_id = Int()
    third_id = Int()
    fourth_id = Int()


class DummyModelSeven(Model):
    """Dummy Model for testing purposes"""

    __storm_table__ = 'dummy_seven'
    id = Int(primary=True)
    second_id = Int(unique=True)
    third_id = Int(index=True)
    fourth_id = Int(index=True, unique=True)


class DummyModelEight(Model):
    """Dummy Model for testing purposes"""

    __storm_table__ = 'dummy_eight'
    __mamba_unique__ = (('second_id', 'third_id'), )
    __mamba_index__ = (('second_id', 'fourth_id'), )
    id = Int(primary=True)
    second_id = Int()
    third_id = Int()
    fourth_id = Int()


class DummyModelEnum(Model):
    """Dummy Model for testing purposes"""

    __storm_table__ = 'dummy_enum'
    id = Int(primary=True)
    mood = Enum(map={'sad': 1, 'ok': 2, 'happy': 3})


class DummyModelNativeEnum(Model):
    """Dummy Model for testing purposes"""

    __storm_table__ = 'dummy_enum'
    id = Int(primary=True)
    mood = NativeEnum(set={'sad', 'ok', 'happy'})


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
