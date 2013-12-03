#!/usr/bin/python
# coding=utf-8
from __future__ import division, print_function, unicode_literals
from copy import deepcopy
from datetime import timedelta
import inspect
import os
import time
from numpy.random import RandomState
from mlite.plots import LivePlot
from .stage import StageFunction
from .utils import generate_seed, create_basic_stream_logger


class Experiment(object):
    CONSTRUCTING, WAITING, RUNNING, COMPLETED, INTERRUPTED, FAILED = range(6)

    def __init__(self, name=None, seed=None, options=None, observers=(),
                 logger=None):
        self.info = dict()
        self.logger = logger
        self.options = options if options is not None else dict()
        self.seed = seed
        self.__doc__ = None
        self.__name__ = name
        self._mainfile = None
        self._main_stage = None
        self._observers = list(observers)
        self._run_seed = None
        self._rnd = None
        self._stages = []
        self._start_time = 0
        self._status = Experiment.CONSTRUCTING

    ################### Observable interface ###################################
    def add_observer(self, obs):
        if not obs in self._observers:
            self._observers.append(obs)

    def remove_observer(self, obs):
        if obs in self._observers:
            self._observers.remove(obs)

    def _emit_created(self):
        for o in self._observers:
            try:
                o.experiment_created_event(name=self.__name__,
                                           stages=self._stages,
                                           seed=self.seed,
                                           mainfile=self._mainfile,
                                           doc=self.__doc__)
            except AttributeError:
                pass

    def _emit_started(self, args, kwargs):
        self.logger.info("Experiment started.")
        self._start_time = time.time()
        for o in self._observers:
            try:
                o.experiment_started_event(start_time=self._start_time,
                                           options=self.options,
                                           run_seed=self._run_seed,
                                           args=args,
                                           kwargs=kwargs,
                                           info=self.info)
            except AttributeError:
                pass
                
    def _emit_info_updated(self):
        for o in self._observers:
            try:
                o.experiment_info_updated(info=self.info)
            except AttributeError:
                pass

    def _emit_completed(self, result):
        stop_time = time.time()
        elapsed_time = timedelta(seconds=round(stop_time - self._start_time))
        self.logger.info("Experiment completed. Took %s", elapsed_time)
        for o in self._observers:
            try:
                o.experiment_completed_event(stop_time=stop_time,
                                             result=result,
                                             info=self.info)
            except AttributeError:
                pass

    def _emit_failed(self):
        self.logger.warning("Experiment aborted!")
        fail_time = time.time()
        for o in self._observers:
            try:
                o.experiment_failed_event(fail_time=fail_time,
                                          info=self.info)
            except AttributeError:
                pass

    def _emit_interrupted(self):
        self.logger.warning("Experiment aborted!")
        interrupt_time = time.time()
        for o in self._observers:
            try:
                o.experiment_interrupted_event(interrupt_time=interrupt_time,
                                               info=self.info)
            except AttributeError:
                pass

    ############################## Decorators ##################################
    def stage(self, f):
        stage_func = StageFunction(f, default_options=self.options)
        self._stages.append(stage_func)
        return stage_func

    def main(self, f):
        self._main_stage = self.stage(f)
        self._mainfile = inspect.getabsfile(f)
        if self.__name__ is None:
            self.__name__ = os.path.basename(self._mainfile).rsplit('.', 1)[0]
        self.__doc__ = inspect.getmodule(f).__doc__
        self._status = Experiment.WAITING
        self._emit_created()
        if f.__module__ == "__main__":
            import sys
            args = sys.argv[1:]
            ######## run main #########
            result = self.run(*args)
            ###########################
            print(result)
            sys.exit(0)
        else:
            f.func_globals['__experiment__'] = self

        return self._main_stage
        
    def live_plot(self, f):
        if not inspect.isgeneratorfunction(f):
            raise TypeError("Live plots must be generator functions!")
        lp = LivePlot(f)
        self.add_observer(lp)
        return lp

    ######################## Experiment public Interface #######################
    def run(self, *args, **kwargs):
        self._initialize()
        self._emit_started(args, kwargs)
        try:
            result = self._main_stage(*args, **kwargs)
            self._status = Experiment.COMPLETED
            self._emit_completed(result)
            return result
        except KeyboardInterrupt:
            self._status = Experiment.INTERRUPTED
            self._emit_interrupted()
            raise
        except:
            self._status = Experiment.FAILED
            self._emit_failed()
            raise

    def _initialize(self):
        self.set_up_logging()
        self._reseed()
        self._status = Experiment.RUNNING

    def _reseed(self):
        if 'seed' in self.options:
            self.seed = self.options['seed']

        if self.seed is None:
            self._run_seed = generate_seed()
            self.logger.warning("No seed given. Using seed=%d. Set in config"
                                " file to repeat experiment.", self._run_seed)
        else:
            self._run_seed = self.seed
        self._rnd = RandomState(self._run_seed)

        for s in self._stages:
            s.seed = generate_seed(self._rnd)

    def set_up_logging(self):
        if self.logger is None:
            self.logger = create_basic_stream_logger(self.__name__)
            self.logger.debug("No logger given. Created basic stream logger.")
        for s in self._stages:
            s.logger = self.logger.getChild(s.__name__)

    ################################## Optionsets ##############################
    def optionset(self, section_name):
        options = deepcopy(self.options)
        options.update(self.options[section_name])
        return OptionContext(options, self._stages)


class StageFunctionOptionsView(object):
    def __init__(self, stage_func, options):
        self.options = options
        self.func = stage_func

    def __call__(self, *args, **kwargs):
        return self.func.execute(args, kwargs, self.options)


class OptionContext(object):
    def __init__(self, options, stage_functions):
        self.options = options
        for sf in stage_functions:
            sf_view = StageFunctionOptionsView(sf, options)
            self.__setattr__(sf.__name__, sf_view)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def keys(self):
        return self.options.keys()

    def __getitem__(self, item):
        return self.options[item]