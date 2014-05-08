# -*- test-case-name: mamba.test.test_logger -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
Mamba logger utilities
"""

from twisted.python import logfile
from storm.tracer import debug as storm_debug


class StormDebugLogFile(logfile.DailyLogFile):
    """Log storm traces to the log directory
    """

    @classmethod
    def start(cls):
        """Start logging
        """

        obj = cls.fromFullPath('logs/storm.log')
        storm_debug(True, stream=obj)

    @staticmethod
    def stop():
        """Stop logging
        """
        storm_debug(False)
