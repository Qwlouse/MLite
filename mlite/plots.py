#!/usr/bin/python
# coding=utf-8

from __future__ import division, print_function, unicode_literals
import inspect
import time
from observers import ExperimentObserver
import matplotlib.pyplot as plt


class LivePlot(ExperimentObserver):
    def __init__(self, live_plot_function, fps=1, stop_at_completion=True):
        if not inspect.isgeneratorfunction(live_plot_function):
            raise TypeError("Live plots must be generator functions!")
        self.f = live_plot_function
        self.f_run = None
        self.fps = fps
        self.last_update = 0
        self.stop_at_completion = stop_at_completion

    def experiment_started_event(self, start_time, options, run_seed, args,
                                 kwargs, info):
        plt.ion()
        self.f_run = self.f()
        self.f_run.next()

    def experiment_info_updated(self, info):
        now = time.time()
        if self.last_update + 1.0/self.fps < now:
            self.f_run.send(info)
            plt.draw()
            self.last_update = now

    def experiment_completed_event(self, stop_time, result, info):

        self.f_run.send(info)
        plt.draw()
        if self.stop_at_completion:
            plt.ioff()
            plt.show()




