#!/usr/bin/python
# coding=utf-8
from __future__ import division, print_function, unicode_literals
import unittest
from ..experiment import Experiment
from ..stage import StageFunction
from mock import Mock


class ExperimentTest(unittest.TestCase):
    def test_constructor_with_name_only(self):
        ex = Experiment('test')
        self.assertEqual(ex.name, 'test')

    def test_experiment_can_decorate_stages(self):
        ex = Experiment('test')

        @ex.stage
        def teststage1():
            return 5

        @ex.stage
        def teststage2():
            return 7

        self.assertIn(teststage1, ex.stages)
        self.assertIn(teststage2, ex.stages)
        self.assertEqual(teststage1(), 5)
        self.assertEqual(teststage2(), 7)

    def test_experiment_decorated_stages_are_stages(self):
        ex = Experiment('test')

        @ex.stage
        def teststage():
            return 5

        self.assertIsInstance(teststage, StageFunction)

    def test_experiment_decorated_stages_inject_options(self):
        ex = Experiment('test', options={'a': 10})

        @ex.stage
        def teststage(a=2):
            return a

        self.assertEqual(teststage(3), 3)
        self.assertEqual(teststage(), 10)
        ex.options['a'] = 23
        self.assertEqual(teststage(), 23)
        del ex.options['a']
        self.assertEqual(teststage(), 2)

    def test_experiment_provides_main_decorator(self):
        ex = Experiment('test')

        @ex.main
        def mainfunc():
            return 25

        self.assertEqual(mainfunc(), 25)
        self.assertEqual(ex.run(), 25)

    def test_experiment_stage_provides_rnd(self):
        ex = Experiment('test')

        @ex.stage
        def randomTest(rnd):
            return rnd.randint(5, 1000000)

        a1 = randomTest()
        a2 = randomTest()
        self.assertGreaterEqual(a1, 5)
        self.assertGreaterEqual(a2, 5)
        self.assertNotEqual(a1, a2)

    def test_auto_rnd_deterministic(self):
        ex = Experiment('test', seed=1234567)

        @ex.stage
        def randomTest1(rnd):
            return rnd.randint(5, 1000000)

        @ex.stage
        def randomTest2(rnd):
            return rnd.randint(5, 1000000)

        @ex.main
        def mainfunc(rnd):
            return rnd.randint(5, 1000000)

        a1 = randomTest1()
        b1 = randomTest2()
        c1 = mainfunc()
        self.assertNotEqual(a1, b1)
        self.assertNotEqual(b1, c1)
        self.assertNotEqual(c1, a1)

        ex.reseed()
        c2 = mainfunc()
        a2 = randomTest1()
        b2 = randomTest2()
        self.assertEqual(a1, a2)
        self.assertEqual(b1, b2)
        self.assertEqual(c1, c2)

    def test_observability(self):
        m = Mock()
        name = 'test1234'
        options = {'foo': 'bar', 'baz': 3}
        ex = Experiment(name, seed=1234567, options=options, observers=[m])
        self.assertTrue(m.experiment_created_event.called)
        m.experiment_created_event.assert_called_with(name, options)
