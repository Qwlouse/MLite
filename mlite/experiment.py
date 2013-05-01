#!/usr/bin/python
# coding=utf-8

from __future__ import division, print_function, unicode_literals
from .stage import StageFunction
from numpy.random import RandomState
import time


class Experiment(object):
    def __init__(self, name, seed=None, options=(), observers=()):
        self.name = name
        self.stages = []
        self.main_stage = None
        self.seed = seed
        self.reseed()
        self.options = options
        self.observers = list(observers)
        self.emit_created()

    ################### Observable interface ###################################
    def emit_created(self):
        for o in self.observers:
            try:
                o.experiment_created_event(self.name, self.options)
            except AttributeError:
                pass

    def emit_started(self, args, kwargs):
        start_time = time.time()
        for o in self.observers:
            try:
                o.experiment_started_event(start_time, self.seed, args, kwargs)
            except AttributeError:
                pass

    def stage(self, f):
        seed = self.rnd.randint(0, 1000000)
        stage_func = StageFunction(f, seed, default_options=self.options)
        self.stages.append(stage_func)
        return stage_func

    def main(self, f):
        self.main_stage = self.stage(f)
        return self.main_stage

    def run(self, *args, **kwargs):
        return self.main_stage(*args, **kwargs)

    def reseed(self):
        if self.seed is None:
            self.rnd = RandomState()
        else:
            self.rnd = RandomState(self.seed)

        for s in self.stages:
            s.seed = self.rnd.randint(0, 1000000)
            s.reseed()
