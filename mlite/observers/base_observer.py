#!/usr/bin/python
# coding=utf-8
from __future__ import division, print_function, unicode_literals


class ExperimentObserver(object):
    def experiment_created_event(self, name, stages, seed, mainfile, doc):
        pass

    def experiment_started_event(self, start_time, options, run_seed, args,
                                 kwargs, info):
        pass

    def experiment_info_updated(self, info):
        pass

    def experiment_completed_event(self, stop_time, result, info):
        pass

    def experiment_aborted_event(self, fail_time, info):
        pass
