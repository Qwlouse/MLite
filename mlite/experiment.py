#!/usr/bin/python
# coding=utf-8
from __future__ import division, print_function, unicode_literals
import inspect
from numpy.random import RandomState
import time
from .stage import StageFunction
from utils import generate_seed


class Experiment(object):
    def __init__(self, name, seed=None, options=(), observers=()):
        self.name = name
        self.stages = []
        self.seed = seed
        self.options = options
        self.observers = list(observers)
        self.main_stage = None
        self.mainfile = None
        self.__doc__ = None

    ################### Observable interface ###################################
    def add_observer(self, obs):
        if not obs in self.observers:
            self.observers.append(obs)

    def remove_observer(self, obs):
        if obs in self.observers:
            self.observers.remove(obs)

    def emit_created(self):
        for o in self.observers:
            try:
                o.experiment_created_event(name=self.name,
                                           options=self.options,
                                           stages=self.stages,
                                           seed=self.seed,
                                           mainfile=self.mainfile,
                                           doc=self.__doc__)
            except AttributeError:
                pass

    def emit_started(self, args, kwargs):
        start_time = time.time()
        for o in self.observers:
            try:
                o.experiment_started_event(start_time=start_time,
                                           run_seed=self.run_seed,
                                           args=args,
                                           kwargs=kwargs)
            except AttributeError:
                pass

    def emit_completed(self, result):
        stop_time = time.time()
        for o in self.observers:
            try:
                o.experiment_completed_event(stop_time, result)
            except AttributeError:
                pass

    def stage(self, f):
        stage_func = StageFunction(f, default_options=self.options)
        self.stages.append(stage_func)
        return stage_func

    def main(self, f):
        self.main_stage = self.stage(f)
        self.mainfile = inspect.getabsfile(f)
        self.__doc__ = inspect.getmodule(f).__doc__
        self.emit_created()
        return self.main_stage

    def run(self, *args, **kwargs):
        self.reseed()
        self.emit_started(args, kwargs)
        result = self.main_stage(*args, **kwargs)
        self.emit_completed(result)
        return result

    def reseed(self):
        if self.seed is None:
            self.run_seed = generate_seed()
        else:
            self.run_seed = self.seed
        self.rnd = RandomState(self.run_seed)

        for s in self.stages:
            s.seed = generate_seed(self.rnd)
