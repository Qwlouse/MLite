#!/usr/bin/python
# coding=utf-8
from __future__ import division, print_function, unicode_literals
import inspect
import os
import time
from numpy.random import RandomState
from .stage import StageFunction
from .utils import generate_seed, create_basic_stream_logger


class Experiment(object):
    CONSTRUCTING, WAITING, RUNNING, COMPLETED, FAILED = range(5)

    def __init__(self, name=None, seed=None, options=(), observers=(),
                 logger=None):
        self.name = name
        self.stages = []
        self.seed = seed
        self.options = options
        self.observers = list(observers)
        self.main_stage = None
        self.mainfile = None
        self.__doc__ = None
        self.logger = logger
        self.status = Experiment.CONSTRUCTING

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
                                           stages=self.stages,
                                           seed=self.seed,
                                           mainfile=self.mainfile,
                                           doc=self.__doc__)
            except AttributeError:
                pass

    def emit_started(self, args, kwargs):
        self.logger.info("Experiment started.")
        start_time = time.time()
        for o in self.observers:
            try:
                o.experiment_started_event(start_time=start_time,
                                           options=self.options,
                                           run_seed=self.run_seed,
                                           args=args,
                                           kwargs=kwargs)
            except AttributeError:
                pass

    def emit_completed(self, result):
        self.logger.info("Experiment completed.")
        stop_time = time.time()
        for o in self.observers:
            try:
                o.experiment_completed_event(stop_time=stop_time,
                                             result=result)
            except AttributeError:
                pass

    def emit_failed(self):
        self.logger.warning("Experiment aborted!")
        fail_time = time.time()
        for o in self.observers:
            try:
                o.experiment_aborted_event(fail_time=fail_time)
            except AttributeError:
                pass
                
    ############################## Decorators ##################################
    def stage(self, f):
        stage_func = StageFunction(f, default_options=self.options)
        self.stages.append(stage_func)
        return stage_func

    def main(self, f):
        self.main_stage = self.stage(f)
        self.mainfile = inspect.getabsfile(f)
        if self.name is None:
            self.name = os.path.basename(self.mainfile).rsplit('.', 1)[0]
        self.__doc__ = inspect.getmodule(f).__doc__
        self.status = Experiment.WAITING
        self.emit_created()
        return self.main_stage
        
    ######################## Experiment public Interface #######################
    def run(self, *args, **kwargs):
        self.initialize()
        self.emit_started(args, kwargs)
        try:
            result = self.main_stage(*args, **kwargs)
            self.status = Experiment.COMPLETED
            self.emit_completed(result)
            return result
        except:
            self.status = Experiment.FAILED
            self.emit_failed()
            raise

    def initialize(self):
        self.set_up_logging()
        self.reseed()
        self.status = Experiment.RUNNING

    def reseed(self):
        if self.seed is None:
            self.run_seed = generate_seed()
            self.logger.warning("No seed given. Using seed=%d. Set in config"
                                " file to repeat experiment", self.run_seed)
        else:
            self.run_seed = self.seed
        self.rnd = RandomState(self.run_seed)

        for s in self.stages:
            s.seed = generate_seed(self.rnd)

    def set_up_logging(self):
        if self.logger is None:
            self.logger = create_basic_stream_logger(self.name)
