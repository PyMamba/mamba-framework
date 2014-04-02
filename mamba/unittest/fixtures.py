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

from storm.schema import schema

from mamba.enterprise.database import Database
from mamba.application.model import ModelManager


class FixtureError(Exception):
    """Raised on fixture errors
    """


class Fixture(schema.Schema):
    """Create, insert, drop and clean table schemas.
    """

    database = Database()

    def __init__(self):
        super(Fixture, self).__init__(
            creates=set(), drops=set(), deletes=set(), patch_package=None)

    @property
    def store(self):
        """Always returns a ready to use valid store
        """

        return Database().store()

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

    def create_testing_tables(self):
        """Create testing tables in the conigured database (if any)
        """

        manager = ModelManager()
        store = self.database().store()
        for model in [m['object'] for m in manager.get_models().values()]:
            store.execute(model.dump_table().replace(
                model.__storm_table__,
                '_mamba_test_{}'.format(model.__storm_table__))
            )

        store.commit()

    def drop_testing_tables(self):
        """Drop testing tables from teh configured database (if any)
        """

        manager = ModelManager()
        store = self.database().store()
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
            store = Database().store()

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

        return self.database.store() if store is None else store
