#!/usr/bin/python
# coding=utf-8
from __future__ import division, print_function, unicode_literals
import unittest
from ..stage import StageFunction


class StageFunctionTest(unittest.TestCase):
    def test_stage_preserves_name_and_doc_string(self):
        def complicated_name():
            """some documentation"""
            pass

        s = StageFunction(complicated_name, 0)
        self.assertEqual(complicated_name.__name__, s.__name__)
        self.assertEqual(complicated_name.__doc__, s.__doc__)

    def test_stage_extracts_source_code(self):
        def complicated_name():
            a = 5 * 7
            return a + 17 + 4

        s = StageFunction(complicated_name, 0)
        self.assertEqual(s._source, """\
        def complicated_name():
            a = 5 * 7
            return a + 17 + 4\n""")

    def test_stage_provides_rnd_argument(self):
        def test(rnd):
            return rnd.randint(5, 1000000)

        test_stage = StageFunction(test, 0)
        a1 = test_stage()
        a2 = test_stage()
        self.assertGreaterEqual(a1, 5)
        self.assertGreaterEqual(a2, 5)
        self.assertNotEqual(a1, a2)

    def test_stage_rnd_deterministic1(self):
        def test(rnd):
            return rnd.randint(5, 1000000)

        test_stage1 = StageFunction(test, 0)
        test_stage2 = StageFunction(test, 0)
        a1 = test_stage1()
        a2 = test_stage2()
        self.assertEqual(a1, a2)

    def test_stage_rnd_deterministic2(self):
        def test(rnd):
            return rnd.randint(5, 1000000)

        test_stage = StageFunction(test, 0)
        a1 = test_stage()
        test_stage.reseed()
        a2 = test_stage()
        self.assertEqual(a1, a2)

    def test_stage_rnd_independent_per_call(self):
        def test(k, rnd):
            return [rnd.randint(5, 1000000) for _ in range(k)]

        test_stage = StageFunction(test, 0)
        test_stage(1)
        a1, = test_stage(1)
        test_stage.reseed()
        test_stage(5)
        a2, = test_stage(1)
        self.assertEqual(a1, a2)