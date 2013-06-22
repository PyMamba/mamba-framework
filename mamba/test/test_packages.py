
# Copyright (c) 2013 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
Tests for mamba.core.packages
"""

import sys
import tempfile

from twisted.trial import unittest
from twisted.python import filepath

from mamba.core import packages, GNU_LINUX
from mamba.application.model import ModelManager
from mamba.application.controller import ControllerManager


class PackagesManagerTest(unittest.TestCase):

    def setUp(self):
        sys.path.append('../mamba/test/dummy_app')

    def test_register_package(self):
        config_file = tempfile.NamedTemporaryFile(delete=False)
        config_file.write(
            '{'
            '   "packages": {'
            '       "fakeshared": {"autoimport": true, "use_scripts": true}'
            '   }'
            ' }'
        )
        config_file.close()
        manager = packages.PackagesManager(config_file=config_file.name)
        if GNU_LINUX:
            mgr = manager.packages['fakeshared']['controller']
            self.addCleanup(mgr.notifier.loseConnection)
            mgr = manager.packages['fakeshared']['model']
            self.addCleanup(mgr.notifier.loseConnection)

        self.assertTrue(manager.config.loaded)
        self.assertEqual(
            manager.config.packages,
            {u'fakeshared': {u'autoimport': True, u'use_scripts': True}}
        )

        pkgs = manager.packages
        self.assertEqual(len(pkgs), 1)
        self.assertIsInstance(
            pkgs['fakeshared']['controller'], ControllerManager)
        self.assertIsInstance(pkgs['fakeshared']['model'], ModelManager)

        filepath.FilePath(config_file.name).remove()
