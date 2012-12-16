
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
Tests for mamba.utils.converter
"""

import json

from twisted.trial import unittest

from mamba.utils.converter import Converter


class ConverterTest(unittest.TestCase):

    def setUp(self):
        self.test_data = {
            int: 1,
            long: 1L,
            float: 1.0,
            bool: True,
            str: 'String',
            unicode: u'Unicode',
            tuple: (1, 2),
            list: [1, 2],
            dict: {}
        }

    def test_converts_primitives_to_json(self):
        for t in set(Converter.primitives + Converter.containers):
            if t is str or t is unicode:
                self.assertEquals(
                    json.dumps(self.test_data[t]),
                    '"{}"'.format(self.test_data[t])
                )
            elif t is bool:
                self.assertEquals(
                    json.dumps(self.test_data[t]),
                    str(self.test_data[t]).lower()
                )
            elif t is tuple:
                self.assertEquals(
                    json.dumps(self.test_data[t]),
                    str(list(self.test_data[t]))
                )
            else:
                self.assertEquals(
                    json.dumps(self.test_data[t]), str(self.test_data[t]))

    def test_convert_object_to_json(self):

        class Collaborator:
            name = 'Collaborator'
            desc = 'This is an object collaborator'
            some_int = 10
            some_float = 10.0

        c1 = {
            'name': 'Collaborator',
            'desc': 'This is an object collaborator',
            'some_int': 10,
            'some_float': 10.0
        }
        c2 = Collaborator()

        self.assertEquals(Converter.serialize(c1), Converter.serialize(c2))

        class Collaborator2(object):
            name = 'Collaborator'
            desc = 'This is an object collaborator'
            some_int = 10
            some_float = 10.0

        c3 = Collaborator2()

        self.assertEquals(Converter.serialize(c1), Converter.serialize(c3))
