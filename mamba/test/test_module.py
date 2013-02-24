
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
Tests for mamba.core.module
"""

from twisted.trial import unittest

from mamba.core import GNU_LINUX
from mamba.core.interfaces import INotifier
from mamba.core.module import ModuleManager


class ModuleManagerTest(unittest.TestCase):
    """
    This is a pure base class so it's hardly tested in its inheritors
    """

    def test_module_manager_implements_inotifier(self):
        if not GNU_LINUX:
            raise unittest.SkipTest('File monitoring only available on Linux')

        self.assertTrue(INotifier.implementedBy(ModuleManager))
