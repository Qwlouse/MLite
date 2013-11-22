#!/usr/bin/python
# coding=utf-8
from __future__ import division, print_function, unicode_literals
from time import sleep

from mlite.experiment import Experiment

ex = Experiment()


@ex.main
def main():
    print("Hello Experiment!")
    sleep(1)
    return 42

