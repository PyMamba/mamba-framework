
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
Tests for L{mamba.project.manager}
"""

from twisted.trial import unittest

from pyDoubles.framework import *
from pyDoubles.matchers import *

from mamba.utils import borg
from mamba.project import manager


class ProjectManagerTest(unittest.TestCase):
    """Tests for L{mamba.project.manager}"""

    def setUp(self):
        self.spy = proxy_spy(manager.ProjectManager({}))

    def test_class_inherits_borg(self):
        mgr = manager.ProjectManager({})
        self.assertTrue(issubclass(type(mgr), borg.Borg))
