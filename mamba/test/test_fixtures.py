
# Copyright (c) 2012 ~ 2014 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""Unit tests for unittesting module helper
"""

import os
import sys

from twisted.trial import unittest

from mamba.core import GNU_LINUX
from mamba.unittest import fixtures
from mamba.application.model import ModelManager


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

    def test_fixture_create_testing_tables(self):
        os.chdir('../mamba/test/dummy_app')
        sys.path.append('.')
        mgr = ModelManager()
        if GNU_LINUX:
            self.addCleanup(mgr.notifier.loseConnection)

        self.fixture.create_testing_tables(mgr=mgr)
        self.assertTrue(
            '_mamba_test_dummy' in [r[0] for r in self.fixture.store.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).get_all()]
        )
        self.assertTrue(
            '_mamba_test_stubing' in [r[0] for r in self.fixture.store.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).get_all()]
        )

        self.fixture.drop_testing_tables(mgr=mgr)

    def test_fixture_drop_testing_tables(self):
        os.chdir('../mamba/test/dummy_app')
        sys.path.append('.')
        mgr = ModelManager()
        if GNU_LINUX:
            self.addCleanup(mgr.notifier.loseConnection)
        self.fixture.create_testing_tables(mgr=mgr)
        self.assertTrue(
            '_mamba_test_dummy' in [r[0] for r in self.fixture.store.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).get_all()]
        )
        self.fixture.drop_testing_tables(mgr=mgr)
        self.assertFalse(
            '_mamba_test_dummy' in [r[0] for r in self.fixture.store.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).get_all()]
        )


class FixturesTestCaseTest(unittest.TestCase):

    def test_setup_patch_modules(self):
        with fixtures.fixture_project('../mamba/test/dummy_app'):
            fixture_test_case = fixtures.FixtureTestCase()
            fixture_test_case.setUp()
            self.assertTrue(all(
                ['_mamba_test_' in m['object'].__storm_table__ for m in
                    fixture_test_case.manager.get_models().values()]
            ))

    def test_tear_down_unpatch_modules(self):
        with fixtures.fixture_project('../mamba/test/dummy_app'):
            fixture_test_case = fixtures.FixtureTestCase()
            fixture_test_case.setUp()
            self.assertTrue(all(
                ['_mamba_test_' in m['object'].__storm_table__ for m in
                    fixture_test_case.manager.get_models().values()]
            ))
            fixture_test_case.tearDown()
            self.assertTrue(all(
                ['_mamba_test_' not in m['object'].__storm_table__ for m in
                    fixture_test_case.manager.get_models().values()]
            ))

    def test_fixture_project_defaults_to_inmediate_directory(self):
        with fixtures.fixture_project():
            self.assertTrue(fixtures.os.path.exists('./_trial_temp'))
