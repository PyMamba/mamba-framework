
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
Tests for mamba.utils.converter
"""

import decimal

from twisted.trial import unittest

from mamba.utils import json
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
                self.assertEqual(
                    json.dumps(self.test_data[t]),
                    '"{}"'.format(self.test_data[t])
                )
            elif t is bool:
                self.assertEqual(
                    json.dumps(self.test_data[t]),
                    str(self.test_data[t]).lower()
                )
            elif t is tuple:
                self.assertEqual(
                    json.dumps(self.test_data[t]).replace(' ', ''),
                    str(list(self.test_data[t])).replace(' ', '')
                )
            else:
                self.assertEqual(
                    json.dumps(self.test_data[t]).replace(' ', ''),
                    str(self.test_data[t]).replace(' ', '')
                )

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

        self.assertEqual(Converter.serialize(c1), Converter.serialize(c2))

        class Collaborator2(object):
            name = 'Collaborator'
            desc = 'This is an object collaborator'
            some_int = 10
            some_float = 10.0

        c3 = Collaborator2()

        self.assertEqual(Converter.serialize(c1), Converter.serialize(c3))

    def test_convert_decimal(self):

        class Collaborator:
            data = decimal.Decimal('1.29')

        self.assertEqual(Converter.serialize(Collaborator()), {'data': '1.29'})

    def test_convert_multi_level(self):

        class Collaborator:
            name = 'C1'

        class Collabortor2:
            name = 'C2'
            child = Collaborator()

        class Collaborator3:
            name = 'C3'
            child = Collabortor2()

        self.assertEqual(
            Converter.serialize(Collaborator3()),
            {'name': 'C3', 'child': {'name': 'C2', 'child': {'name': 'C1'}}}
        )

    def test_can_convert_non_static_properties_in_objects(self):

        class Collaborator:
            def __init__(self, name):
                self.name = name

        self.assertEqual(
            Converter.serialize(Collaborator('C1')), {'name': 'C1'})

        c2 = Collaborator('C2')
        c2.size = 3
        self.assertEqual(Converter.serialize(c2), {'name': 'C2', 'size': 3})
        c3 = Collaborator('C3')
        c3.collaborator = c2
        c3.pene = decimal.Decimal('10.0')

        self.assertEqual(Converter.serialize(c3), {
            'collaborator': {
                'name': 'C2', 'size': 3}, 'pene': '10.0', 'name': 'C3'
        })
