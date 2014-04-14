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

from mamba.enterprise import schema
from mamba.unittest.database_helpers import TestableDatabase, ENGINE


class FixtureError(Exception):
    """Raised on fixture errors
    """


class Fixture(schema.Schema):
    """Create, insert, drop and clean table schemas.
    """

    def __init__(self, model=None, path='../', engine=ENGINE.NATIVE):
        super(Fixture, self).__init__(
            creates=set(), drops=set(), deletes=set(), patch_package=None)

        self._path = path
        self._model = model
        self._original_database = None
        self.testable_database = TestableDatabase(engine)

        if self._model is not None:
            self._original_database = self._model.database
            self._model.database = self.testable_database

    def __enter__(self):
        """Enter the fixture context
        """

        self._currdir = os.getcwd()
        if '_trial_temp' not in self._currdir:
            raise FixtureError('Fixture context must be used in tests only')

        os.chdir(self._path)
        return self

    def __exit__(self, ext, exv, trb):
        """Leave the fixture context
        """

        os.chdir(self._currdir)
        if self._original_database is not None:
            self._model.database = self._original_database

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
