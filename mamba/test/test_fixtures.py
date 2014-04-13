
# Copyright (c) 2012 ~ 2014 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""Unit tests for unittesting module helper
"""

import os

from twisted.trial import unittest

from mamba.unittest import fixtures
from mamba.application.model import Model

orig_testable = fixtures.TestableDatabase


class FakeTesttableDatabase(object):

    def __init__(self, engine=None):
        self.engine = engine


class FixturesTest(unittest.TestCase):

    def setUp(self):
        self.currdir = os.getcwd()
        self.fixture = fixtures.Fixture()

    def tearDown(self):
        os.chdir(self.currdir)

    def test_fixtures_constructs_empty_sets(self):
        self.assertEqual(self.fixture._creates, set())
        self.assertEqual(self.fixture._drops, set())
        self.assertEqual(self.fixture._deletes, set())

    def test_fixtures_constructs_none_patch_package(self):
        self.assertIsNone(self.fixture._patch_package)

    def test_fixtures_add_create(self):
        self.fixture.add_create('CREATE TABLE dummy;')
        self.assertSetEqual(
            self.fixture._creates, set(['CREATE TABLE dummy;']))

    def test_fixtures_add_create_raises_exception_on_wrong_query(self):
        self.assertRaises(
            fixtures.FixtureError, self.fixture.add_create, 'DROP TABLE dummy;'
        )

    def test_fixtures_add_create_non_duplicates(self):
        self.fixture.add_create('CREATE TABLE dummy;')
        self.assertSetEqual(
            self.fixture._creates, set(['CREATE TABLE dummy;']))
        self.fixture.add_create('CREATE TABLE dummy;')
        self.assertSetEqual(
            self.fixture._creates, set(['CREATE TABLE dummy;']))
        self.fixture.add_create('CREATE TABLE dummy2;')
        self.assertSetEqual(
            self.fixture._creates,
            set(['CREATE TABLE dummy;', 'CREATE TABLE dummy2;'])
        )

    def test_fixtures_add_drop(self):
        self.fixture.add_drop('DROP TABLE dummy;')
        self.assertSetEqual(self.fixture._drops, set(['DROP TABLE dummy;']))

    def test_fixtures_add_drop_raises_exception_on_wrong_query(self):
        self.assertRaises(
            fixtures.FixtureError, self.fixture.add_drop, 'CREATE TABLE dummy;'
        )

    def test_fixtures_add_drop_non_duplicates(self):
        self.fixture.add_drop('DROP TABLE dummy;')
        self.assertSetEqual(
            self.fixture._drops, set(['DROP TABLE dummy;']))
        self.fixture.add_drop('DROP TABLE dummy;')
        self.assertSetEqual(
            self.fixture._drops, set(['DROP TABLE dummy;']))
        self.fixture.add_drop('DROP TABLE dummy2;')
        self.assertSetEqual(
            self.fixture._drops,
            set(['DROP TABLE dummy;', 'DROP TABLE dummy2;'])
        )

    def test_fixtures_add_delete(self):
        self.fixture.add_delete('DELETE FROM dummy;')
        self.assertSetEqual(self.fixture._deletes, set(['DELETE FROM dummy;']))

    def test_fixtures_add_delete_raises_exception_on_wrong_query(self):
        self.assertRaises(
            fixtures.FixtureError, self.fixture.add_delete, 'DROP TABLE dummy;'
        )

    def test_fixtures_add_delete_non_duplicates(self):
        self.fixture.add_delete('DELETE FROM TABLE dummy;')
        self.assertSetEqual(
            self.fixture._deletes, set(['DELETE FROM TABLE dummy;']))
        self.fixture.add_delete('DELETE FROM TABLE dummy;')
        self.assertSetEqual(
            self.fixture._deletes, set(['DELETE FROM TABLE dummy;']))
        self.fixture.add_delete('DELETE FROM TABLE dummy2;')
        self.assertSetEqual(
            self.fixture._deletes,
            set(['DELETE FROM TABLE dummy;', 'DELETE FROM TABLE dummy2;'])
        )

    def test_fixture_context_returns_himself_when_as_is_used(self):
        with fixtures.Fixture() as fxt:
            self.assertIsInstance(fxt, fixtures.Fixture)

    def test_fixture_context_raises_fixture_error_on_wrong_path(self):
        os.chdir('../')
        try:
            with fixtures.Fixture():
                pass
        except fixtures.FixtureError as error:
            self.assertEqual(
                error[0], 'Fixture context must be used in tests only')
            os.chdir('_trial_temp')

    def test_fixture_context_defaults_to_inmediate_directory(self):

        with fixtures.Fixture():
            self.assertTrue(fixtures.os.path.exists('./_trial_temp'))

    def test_fixture_context_uses_path_if_given(self):

        with fixtures.Fixture(path='../mamba/test/dummy_app'):
            self.assertEqual(os.path.split(os.getcwd())[1], 'dummy_app')

    def test_fixture_context_model_prepate_for_test_if_given(self):

        fixtures.TestableDatabase = FakeTesttableDatabase
        with fixtures.Fixture(model=Model) as fxt:
            self.assertIsInstance(fxt._model.database, FakeTesttableDatabase)
            self.assertIs(fxt._model.database, Model.database)
        fixtures.TestableDatabase = orig_testable

    def test_fixture_context_model_engine_is_set_if_given(self):

        fixtures.TestableDatabase = FakeTesttableDatabase
        with fixtures.Fixture(
                model=Model, engine=fixtures.ENGINE.NATIVE) as fxt:
            self.assertIs(fxt._model.database.engine, fixtures.ENGINE.NATIVE)

        fixtures.TestableDatabase = orig_testable

    def test_fixture_context_model_database_come_back_on_leave(self):

        database = None
        fixtures.TestableDatabase = FakeTesttableDatabase
        with fixtures.Fixture(model=Model) as fxt:
            database = fxt._original_database
            self.assertIsInstance(fxt._model.database, FakeTesttableDatabase)
            self.assertIs(fxt._model.database, Model.database)

        fixtures.TestableDatabase = orig_testable
        self.assertIs(Model.database, database)

    def test_fixture_context_path_comes_back_on_leave(self):

        with fixtures.Fixture():
            self.assertTrue(os.path.exists('./_trial_temp'))

        self.assertTrue(not os.path.exists('./_trial_temp'))
        self.assertEqual(os.path.split(os.getcwd())[1], '_trial_temp')

    def test_fixture_project_defaults_to_inmediate_directory(self):
        with fixtures.fixture_project():
            self.assertTrue(os.path.exists('./_trial_temp'))
