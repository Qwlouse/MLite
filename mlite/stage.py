#!/usr/bin/python
# coding=utf-8
from datetime import timedelta
import inspect
import time
from numpy.random import RandomState

from .signature import Signature
from mlite.utils import generate_seed


class StageFunction(object):
    def __init__(self, f, default_options=()):
        self.logger = None
        self.__doc__ = f.__doc__
        self.__name__ = f.__name__
        self._default_options = default_options
        self._seed = None
        self._signature = Signature(f)
        self._source = str(inspect.getsource(f))
        self._wrapped_function = f

    @property
    def seed(self):
        return self._seed

    @seed.setter
    def seed(self, new_seed):
        self._seed = new_seed
        self.rnd = RandomState(self.seed)

    def execute(self, args, kwargs, options):
        opt = dict()
        opt.update(options)
        if 'rnd' in self._signature.arguments:
            seed = generate_seed(self.rnd)
            opt['rnd'] = RandomState(seed)
        args, kwargs = self._signature.construct_arguments(args, kwargs, opt)
        start_time = time.time()
        # self.emit('stage_started', self.__name__, start_time, args, kwargs)
        self.logger.info("Stage started.")
        ####################### run actual function ############################
        result = self._wrapped_function(*args, **kwargs)
        ########################################################################
        stop_time = time.time()
        elapsed_time = timedelta(seconds=round(stop_time - start_time))
        self.logger.info("Stage completed after %s.", elapsed_time)
        # self.emit('stage_completed', self.__name__, stop_time)
        return result

    def __call__(self, *args, **kwargs):
        return self.execute(args, kwargs, self._default_options)