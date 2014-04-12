# -*- test-case-name: mamba.test.test_fixtures -*-
# Copyright (c) 2012 - 2014 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: fixtures
    :paltform: Unix, Windows
    :synopsis: Wrapper around Storm patch/schema mechanism to make mamba model
               objects testing easier

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>
"""

import os
from contextlib import contextmanager

from twisted.trial import unittest

from mamba.core import GNU_LINUX
from mamba.enterprise import schema
from mamba.application.model import ModelManager
from mamba.unittest.database_helpers import TestableDatabase


class FixtureError(Exception):
    """Raised on fixture errors
    """


class Fixture(schema.Schema):
    """Create, insert, drop and clean table schemas.
    """

    testable_database = TestableDatabase()

    def __init__(self, base_path=None):
        super(Fixture, self).__init__(
            creates=set(), drops=set(), deletes=set(), patch_package=None)

    @property
    def store(self):
        """Always returns a ready to use valid store
        """

        return self.testable_database.store()

    def add_create(self, query):
        """Adds a new create query to the create queries set

        :param query: the query to be added
        :type query: str
        """

        if 'CREATE' not in query.upper():
            raise FixtureError(
                'Only CREATE queries are allowed on add_create method'
            )

        self._creates.add(query)

    def add_drop(self, query):
        """Adds a new drop query to the drop queries set

        :param query: the query to be added
        :type query: str
        """

        if 'DROP' not in query.upper():
            raise FixtureError(
                'Only DROP queries are allowed on add_drop method'
            )

        self._drops.add(query)

    def add_delete(self, query):
        """Adds a new delete query to the delete queries set

        :param query: the query to be added
        :type query: str
        """

        if 'DELETE' not in query.upper():
            raise FixtureError(
                'Only DELETE queries are allowed on add_delete method'
            )

        self._deletes.add(query)

    def create_testing_tables(self, store=None, mgr=None):
        """Create testing tables in the conigured database (if any)

        :param store: an optional store to being used
        :type store: :class:`mamba.enterprise.Store`
        """

        manager = ModelManager() if mgr is None else mgr
        store = self._valid_store(store)
        for model in [m['object'] for m in manager.get_models().values()]:
            store.execute(model.dump_table().replace(
                model.__storm_table__,
                '_mamba_test_{}'.format(model.__storm_table__))
            )

        store.commit()

    def drop_testing_tables(self, store=None, mgr=None):
        """Drop testing tables from the configured database (if any)

        :param store: an optional store to being used
        :type store: :class:`mamba.enterprise.Store`
        """

        manager = ModelManager() if mgr is None else mgr
        store = self._valid_store(store)
        for model in [m['object'] for m in manager.get_models().values()]:
            store.execute(model.get_adapter().drop_table().replace(
                model.__storm_table__,
                '_mamba_test_{}'.format(model.__storm_table__))
            )

        store.commit()

    def create(self, store=None):
        """Run CREATE TABLE SQL statements using the given store (if any)

        :param store: the store to use
        :type store: :class:`storm.store.Store`
        """

        if store is None:
            store = self.database.store()

        super(Fixture, self).create(self._valid_store(store))

    def drop(self, store=None):
        """Run DROP TABLE SQL statements using the given store (if any)

        :param store: ths store to use
        :type store: :class:`storm.store.Store`
        """

        super(Fixture, self).drop(self._valid_store(store))

    def delete(self, store=None):
        """Run DELETE FROM SQL statements using the given store (if any)

        :param store: ths store to use
        :type store: :class:`storm.store.Store`
        """

        super(Fixture, self).delete(self._valid_store(store))

    def upgrade(self, store):
        """We don't upgrade fixtures
        """
        pass

    def _valid_store(self, store):
        """Return a valid store always
        """

        return self.testable_database.store() if store is None else store


class FixtureTestCase(unittest.TestCase):

    def __init__(self, methodName='runTest'):
        super(FixtureTestCase, self).__init__(methodName)
        self.database = None

    def setUp(self):
        store = self.base_path if hasattr(self, 'base_path') else None
	if not hasattr(self, 'manager'):
	    self.manager = ModelManager(store=store)

        if GNU_LINUX:
            self.addCleanup(self.manager.notifier.loseConnection)

        self._patch_models()

    def tearDown(self):
        self._unpatch_models()

    def _patch_models(self):
        """Patch models to use TestableDatabase
        """

        for model in [m['object'] for m in self.manager.get_models().values()]:
            if self.database is None:
                self.database = model.database

            model.__storm_table__ = '_mamba_test_{}'.format(
                model.__storm_table__)
            model.database = Fixture.testable_database

    def _unpatch_models(self):
        """Unpatch models that use TestableDatabase
        """

        for model in [m['object'] for m in self.manager.get_models().values()]:
            model.__storm_table__ = model.__storm_table__.replace(
                '_mamba_test_', '')

            if self.database is not None:
                model.database = self.database


@contextmanager
def fixture_project(path='../'):
    """Chdir to the given path, yield and chdir to the previous path
    """

    currdir = os.getcwd()
    if '_trial_temp' not in currdir:
        raise RuntimeError('fixture_project must be used in tests only')

    os.chdir(path)
    yield
    os.chdir(currdir)
