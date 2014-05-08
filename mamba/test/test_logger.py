
# Copyright (c) 2013 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
Tests for mamba.utils.logger
"""

import os

from twisted.trial import unittest

from mamba.utils import logger


class StormDebugLogFileTest(unittest.TestCase):

    def setUp(self):
        os.mkdir('logs')
        self.flag = None
        self.stream = None
        self._storm_debug = logger.storm_debug
        logger.storm_debug = self.storm_debug

    def storm_debug(self, flag, stream=None):
        self.flag = flag
        self.stream = stream

    def tearDown(self):
        logger.storm_debug = self._storm_debug
        os.remove('logs/storm.log')
        os.rmdir('logs')

    def test_start(self):
        logger.StormDebugLogFile.start()
        self.assertTrue(self.flag)
        self.assertIsInstance(self.stream, logger.StormDebugLogFile)
        self.assertTrue(os.path.exists('logs/storm.log'))

    def test_stop(self):
        self.test_start()
        logger.StormDebugLogFile.stop()
        self.assertFalse(self.flag)
