#!/usr/bin/python
# coding=utf-8
from __future__ import division, print_function, unicode_literals
import inspect
import time
import matplotlib.pyplot as plt
from .observers import ExperimentObserver


class LivePlot(ExperimentObserver):
    def __init__(self, live_plot_function, fps=1, stop_at_completion=True):
        if not inspect.isgeneratorfunction(live_plot_function):
            raise TypeError("Live plots must be generator functions!")
        self.f = live_plot_function
        self.f_run = None
        self.fig = None
        self.fps = fps
        self.last_update = 0
        self.stop_at_completion = stop_at_completion

    def start_plot(self):
        plt.ion()
        self.f_run = self.f()
        self.fig = self.f_run.next()

    def update_plot(self, info):
        self.f_run.send(info)
        self.fig.canvas.draw()
        self.last_update = time.time()

    def experiment_info_updated(self, info):
        if self.f_run is None:
            self.start_plot()
        if self.last_update + 1.0/self.fps < time.time():
            self.update_plot(info)

    def experiment_completed_event(self, stop_time, result, info):
        self.update_plot(info)
        if self.stop_at_completion:
            plt.ioff()
            plt.show()




