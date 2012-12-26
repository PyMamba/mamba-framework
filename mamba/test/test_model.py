
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
Tests for mamba.application.model
"""

from twisted.trial import unittest
from storm.locals import Int, Unicode
from storm.twisted.testing import FakeThreadPool
from twisted.internet.defer import inlineCallbacks

from mamba import Model
from mamba import Database


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


class DummyModel(Model):
    """Dummy Model for testing purposes"""

    __storm_table__ = 'dummy'
    id = Int(primary=True)
    name = Unicode()

    def __init__(self, name=None):
        super(DummyModel, self).__init__()

        if name is not None:
            self.name = unicode(name)


class DummyThreadPool(FakeThreadPool):

    def start(self):
        pass

    def stop(self):
        pass
