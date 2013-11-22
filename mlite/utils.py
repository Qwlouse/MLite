#!/usr/bin/python
# coding=utf-8
from __future__ import division, print_function, unicode_literals
import logging
import sys
import numpy as np

SEED_RANGE = 0, sys.maxsize // 10000


def generate_seed(rnd=None):
    if rnd is None:
        return np.random.randint(*SEED_RANGE)
    else:
        return rnd.randint(*SEED_RANGE)


def create_basic_stream_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers = []
    ch = logging.StreamHandler()
    ch.setLevel(level)
    formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger

NO_LOGGER = logging.getLogger('ignore')
NO_LOGGER.disabled = 1