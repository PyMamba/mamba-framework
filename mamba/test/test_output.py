
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
Tests for mamba.utils.output
"""

from twisted.trial import unittest

from mamba.utils.output import codes, _styles, style_to_ansi_code


class TestOutput(unittest.TestCase):

    def test_colors(self):
        for color in codes.keys():
            if color not in ['normal', 'reset', 'underline', 'overline']:
                objs = [color]
                module_color = __import__(
                    'mamba.utils.output', globals(), locals(), objs
                )
                test_color = getattr(module_color, objs[0])

                if color in codes:
                    the_color = codes[color] + 'Test' + codes['reset']
                elif color in _styles:
                    the_color = (
                        style_to_ansi_code(color) + 'Test' + codes['reset']
                    )
                else:
                    the_color = 'Test'

                self.assertEqual(test_color('Test'), the_color)

        self.flushLoggedErrors()
