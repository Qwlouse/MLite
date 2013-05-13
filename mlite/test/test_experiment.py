#!/usr/bin/python
# coding=utf-8
"""
Some tests for the experiment class
"""

from __future__ import division, print_function, unicode_literals
from mock import Mock
import unittest
import time
from ..experiment import Experiment
from ..stage import StageFunction


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

        ex.reseed()
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

        ex.reseed()
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

    def test_auto_rnd_with_seed_deterministic_per_run(self):
        ex = Experiment('test', seed=1234567)

        @ex.stage
        def randomTest(rnd):
            return rnd.randint(5, 1000000)

        @ex.main
        def mainfunc(rnd):
            return randomTest() + rnd.randint(5, 1000000)

        a = ex.run()
        b = ex.run()
        self.assertEqual(a, b)

    def test_auto_rnd_without_seed_is_random_per_run(self):
        ex = Experiment('test')

        @ex.stage
        def randomTest(rnd):
            return rnd.randint(5, 1000000)

        @ex.main
        def mainfunc(rnd):
            return randomTest() + rnd.randint(5, 1000000)

        a = ex.run()
        b = ex.run()
        self.assertNotEqual(a, b)

    def test_add_observer(self):
        ex = Experiment('name')
        m = object()
        ex.add_observer(m)
        self.assertIn(m, ex.observers)

    def test_add_observer_twice(self):
        ex = Experiment('name')
        m = object()
        ex.add_observer(m)
        ex.add_observer(m)
        self.assertEqual(ex.observers.count(m), 1)

    def test_remove_nonobserver(self):
        ex = Experiment('name')
        m = object()
        self.assertNotIn(m, ex.observers)
        ex.remove_observer(m)
        self.assertNotIn(m, ex.observers)

    def test_add_and_remove_observer(self):
        ex = Experiment('name')
        m = object()
        ex.add_observer(m)
        ex.remove_observer(m)
        self.assertNotIn(m, ex.observers)

    def test_experiment_created_event(self):
        m = Mock()
        name = 'test1234'
        ex = Experiment(name, seed=17)
        ex.add_observer(m)

        @ex.stage
        def foo(rnd):
            return rnd.randint(5, 1000000)

        @ex.main
        def bar(rnd):
            return rnd.randint(5, 1000000)

        self.assertTrue(m.experiment_created_event.called)
        m.experiment_created_event.assert_called_with(name=name,
                                                      stages=[foo, bar],
                                                      mainfile=__file__,
                                                      seed=17,
                                                      doc=__doc__)

    def test_experiment_start_completed_events(self):
        t1 = time.time()
        m = Mock()
        options = {'foo': 'bar', 'baz': 3}
        ex = Experiment('test1234', seed=12345, options=options)
        ex.add_observer(m)

        @ex.main
        def bar(a, b, c):
            return 7

        ex.run(1, 2, c=3)
        t2 = time.time()

        self.assertTrue(m.experiment_started_event.called)
        call_kwargs = m.experiment_started_event.call_args[1]
        self.assertEqual(call_kwargs['options'], options)
        self.assertEqual(call_kwargs['run_seed'], 12345)
        self.assertEqual(call_kwargs['args'], (1, 2))
        self.assertEqual(call_kwargs['kwargs'], {'c': 3})
        start_time = call_kwargs['start_time']
        self.assertGreaterEqual(start_time, t1)
        self.assertGreaterEqual(t2, start_time)

        self.assertTrue(m.experiment_completed_event.called)
        call_kwargs = m.experiment_completed_event.call_args[1]
        self.assertEqual(call_kwargs['result'], 7)
        stop_time = call_kwargs['stop_time']
        self.assertGreaterEqual(stop_time, t1)
        self.assertGreaterEqual(t2, stop_time)
        self.assertGreaterEqual(stop_time, start_time)


