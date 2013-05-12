#!/usr/bin/python
# coding=utf-8
import inspect

from numpy.random import RandomState

from .signature import Signature
from mlite.utils import generate_seed


class StageFunction(object):
    def __init__(self, f, default_options=()):
        self.__name__ = f.__name__
        self.__doc__ = f.__doc__
        self.f = f
        self._seed = None
        self._default_options = default_options
        self._signature = Signature(f)
        self._source = str(inspect.getsource(f))

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
        # start_time = time.time()
        # self.emit('stage_started', self.__name__, start_time, args, kwargs)
        result = self.f(*args, **kwargs)
        # stop_time = time.time()
        # self.emit('stage_completed', self.__name__, stop_time)
        return result

    def __call__(self, *args, **kwargs):
        return self.execute(args, kwargs, self._default_options)