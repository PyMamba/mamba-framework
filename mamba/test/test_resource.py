
# Copyright (c) 2013 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
Tests for mamba.core.resource
"""

import os

from twisted.trial import unittest
from twisted.web.resource import NoResource
from twisted.python.filepath import FilePath

from mamba.core.resource import Resource, Assets


class ResourceTest(unittest.TestCase):

    def test_resource(self):
        resource = Resource()
        self.assertIsInstance(resource.render_keys, dict)
        self.assertEqual(resource.render_keys['doctype'], 'html')
        assert(resource._styles_manager)
        assert(resource._scripts_manager)


class AssetsTest(unittest.TestCase):

    def setUp(self):
        self.assets = Assets(['/dummy'])

    def test_assets(self):

        self.assertEqual(self.assets.paths, [FilePath('/dummy')])

    def test_add_paths(self):

        self.assets.add_paths(['./dummy2'])
        self.assertEqual(
            self.assets.paths[1], FilePath(os.path.abspath('./dummy2')))

    def test_get_child(self):

        self.assets.add_paths(['../mamba/test/dummy_app/static'])
        self.assertIsInstance(
            self.assets.getChild('favicon.ico', None), FilePath)

    def test_get_child_invalid(self):

        self.assertIsInstance(
            self.assets.getChild('invalid', None), NoResource)

    def test_get_child_return_self_on_empty_path(self):

        self.assertIs(self.assets.getChild('', None), self.assets)

    def test_render_returns_empty_string(self):

        self.assertEqual(self.assets.render_GET(None), '')

    def test_render_head_is_render_get(self):

        self.assertEqual(self.assets.render_HEAD, self.assets.render_GET)
