
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
Tests for mamba.core.decorators
"""

from twisted.trial import unittest

from mamba.core import decorators

hit_count = 0


class TestDecorators(unittest.TestCase):

    def setUp(self):
        global hit_count
        hit_count = 0

    def test_cache_is_cahing(self):

        @decorators.cache(size=16)
        def multiplication(a, b):
            global hit_count
            hit_count += 1

            return a * b

        self.assertEqual(multiplication(2, 2), 4)
        self.assertEqual(hit_count, 1)
        self.assertEqual(multiplication(2, 2), 4)
        self.assertEqual(hit_count, 1)
        self.assertEqual(multiplication(4, 4), 16)
        self.assertEqual(hit_count, 2)

    def test_cache_limit_works(self):
        global hit_count

        @decorators.cache(size=2)
        def eat_memory(ignore):
            global hit_count
            hit_count += 1

            return bytearray(1024 * 1024)

        eat_memory(1)
        self.assertEqual(hit_count, 1)
        eat_memory(1)
        self.assertEqual(hit_count, 1)
        eat_memory(2)
        self.assertEqual(hit_count, 2)
        eat_memory(3)
        self.assertEqual(hit_count, 3)
        eat_memory(4)
        self.assertEqual(hit_count, 4)
        eat_memory(1)
        self.assertEqual(hit_count, 5)
