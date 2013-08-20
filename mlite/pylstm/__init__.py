#!/usr/bin/python
# coding=utf-8

from __future__ import division, print_function, unicode_literals
import numpy as np
import matplotlib.pyplot as plt
from ..plots import LivePlot


class InfoUpdater(object):
    def __init__(self, experiment):
        self.ex = experiment

    def __call__(self, epoch, net, training_errors, validation_errors):
        self.ex.info['epochs_needed'] = epoch
        self.ex.info['training_errors'] = training_errors
        self.ex.info['validation_errors'] = validation_errors
        if 'nr_parameters' not in self.ex.info:
            self.ex.info['nr_parameters'] = net.get_param_size()
        if 'architecture' not in self.ex.info:
            self.ex.info['architecture'] = net.architecture
        self.ex._emit_info_updated()


def get_min_err(errors):
    min_epoch = np.argmin(errors)
    return min_epoch, errors[min_epoch]


def plot_train_and_val_error():
    fig, ax = plt.subplots()
    ax.set_title('Training Progress')
    ax.set_xlabel('Epochs')
    ax.set_ylabel('Error')
    info = yield fig
    t_line = None
    v_line = None
    v_dot = None
    if 'training_errors' in info:
        t_line, = ax.plot(info['training_errors'], 'g-', label='Training Error')
    if 'validation_errors' in info and len(info['validation_errors']) > 0:
        val_err = info['validation_errors']
        v_line, = ax.plot(val_err, 'b-', label='Validation Error')
        min_ep, min_err = get_min_err(val_err)
        v_dot, = ax.plot([min_ep], min_err, 'bo')
    ax.legend()
    while True:
        info = yield fig
        if t_line is not None:
            train_err = info['training_errors']
            t_line.set_ydata(train_err)
            t_line.set_xdata(range(len(train_err)))
        if v_line is not None:
            val_err = info['validation_errors']
            v_line.set_ydata(val_err)
            v_line.set_xdata(range(len(val_err)))
            min_ep, min_err = get_min_err(val_err)
            v_dot.set_ydata([min_err])
            v_dot.set_xdata([min_ep])
        ax.relim()
        ax.autoscale_view()

TrainingProgressPlot = LivePlot(plot_train_and_val_error,
                                fps=2,
                                stop_at_completion=False)


class StoreBestWeights(object):
    def __init__(self, ex):
        self.ex = ex

    def __call__(self, epoch, net, training_errors, validation_errors):
        e = validation_errors if len(validation_errors) > 0 else training_errors
        if np.argmin(e) == len(e) - 1:
            self.ex.info['weights'] = net.param_buffer.copy()
            self.ex._emit_info_updated()