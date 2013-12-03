
# Copyright (c) 2013 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
Tests for mamba.utils.heroku
"""

import os
from twisted.trial import unittest

from mamba.utils import heroku


class TestHeroku(unittest.TestCase):

    def test_are_we_on_heroku(self):

        self.assertFalse(heroku.are_we_on_heroku())
        os.environ['PYTHONHOME'] = '/app/.heroku/python'
        self.assertTrue(heroku.are_we_on_heroku())
        del os.environ['PYTHONHOME']
