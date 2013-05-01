#!/usr/bin/python
# coding=utf-8
import inspect
import time
from .signature import Signature
from numpy.random import RandomState


class StageFunction(object):
    def __init__(self, f, seed, default_options=()):
        self.__name__ = f.__name__
        self.__doc__ = f.__doc__
        self.f = f
        self.seed = seed
        self.reseed()
        self._default_options = default_options
        self._signature = Signature(f)
        self._source = str(inspect.getsource(f))

    def reseed(self):
        self.rnd = RandomState(self.seed)

    def execute(self, args, kwargs, options):
        opt = dict()
        opt.update(options)
        opt['rnd'] = RandomState(self.rnd.randint(0, 1000))
        args, kwargs = self._signature.construct_arguments(args, kwargs, opt)
        # start_time = time.time()
        # self.emit('stage_started', self.__name__, start_time, args, kwargs)
        result = self.f(*args, **kwargs)
        # stop_time = time.time()
        # self.emit('stage_completed', self.__name__, stop_time)
        return result

    def __call__(self, *args, **kwargs):
        return self.execute(args, kwargs, self._default_options)