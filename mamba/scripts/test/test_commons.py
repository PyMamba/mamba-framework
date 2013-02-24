
# Copyright (c) 2012 - 2013 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
Tests for mamba.scripts.mamba_admin and subcommands
"""

import sys
from cStringIO import StringIO

from twisted.trial import unittest

from mamba.scripts import commons


class InteractionTest(unittest.TestCase):

    def setUp(self):
        def fake_exit(value):
            pass

        self.stdout = sys.stdout
        self.capture = StringIO()
        sys.stdout = self.capture

        self.exit = sys.exit
        sys.exit = fake_exit

    def tearDown(self):
        sys.stdout = self.stdout
        sys.exit = self.exit

    def test_userquery(self):
        commons.raw_input = lambda _: 'Yes'
        value = commons.Interaction.userquery('Test?')
        self.assertEqual(self.capture.getvalue(), '\nTest? ')
        self.assertEqual(value, 'Yes')

    def test_userquery_wrong_colors_number(self):
        commons.Interaction.userquery('Fail', ('Yes', 'No', 'Maybe'))
        self.assertEqual(
            self.capture.getvalue(),
            '\nFail Response number is greater than colors tuple\n'
        )

    def test_userquery_bad_response(self):
        commons.Interaction.userquery('Fail', 'Yes')
        self.assertEqual(
            self.capture.getvalue().split('\n')[0],
            'Error: response must be tuple or list'
        )

    def test_userquery_bad_colors(self):
        commons.Interaction.userquery('Fail', ('Yes',), 'Red')
        self.assertEqual(
            self.capture.getvalue().split('\n')[0],
            'Error: colors must be tuple or list'
        )

    def test_userquery_three_arguments(self):
        commons.raw_input = lambda _: 'Maybe'
        value = commons.Interaction.userquery(
            'Test?', ('Yes', 'No', 'Maybe'), ('green', 'red', 'brown'))
        self.assertEqual(self.capture.getvalue(), '\nTest? ')
        self.assertEqual(value, 'Maybe')

    def test_userchoice(self):
        commons.raw_input = lambda _: '1'
        value = commons.Interaction.userchoice(
            'Test?', ('One', 'Two'), ('Option One', 'Option Two'))
        self.assertEqual(
            self.capture.getvalue(),
            '\nTest?\n\x1b[34;01mOption One                    '
            '\x1b[39;49;00m [\x1b[01m0\x1b[39;49;00m] \n'
            '\x1b[34;01mOption Two                    \x1b[39;49;00m '
            '[\x1b[01m1\x1b[39;49;00m] \n'
        )
        self.assertEqual(value, 'Two')

    def test_userchoice_none_raise_typerror(self):
        self.assertRaises(TypeError, commons.Interaction.userchoice, 'Fail')

    def test_userchoice_choices_and_help_different_length_raises(self):
        self.assertRaises(
            RuntimeError, commons.Interaction.userchoice, 'Fail', None, None)

    def test_userchoice_choices_and_help_diferent_lenght_raises(self):
        self.assertRaises(
            RuntimeError, commons.Interaction.userchoice, 'Fail', ('1'), ())

    def test_userchoice_choices_and_help_empty_raises(self):
        self.assertRaises(
            RuntimeError, commons.Interaction.userchoice, 'Fail', (), ())

    def test_userinput(self):
        commons.raw_input = lambda _: 'Oh yeah!'
        value = commons.Interaction.userinput('Is this a test?')
        self.assertEqual(
            self.capture.getvalue(),
            '\n\x1b[01mIs this a test?\x1b[39;49;00m\n'
        )
        self.assertEqual(value, 'Oh yeah!')
