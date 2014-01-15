#!/usr/bin/python
# coding=utf-8
from __future__ import division, print_function, unicode_literals
from copy import deepcopy
import cPickle
import numpy as np
import time

try:
    from pymongo import MongoClient
    from pymongo.son_manipulator import SONManipulator
    from bson import Binary
except ImportError:
    raise ImportError('This Observer depends on the pymongo package. '
                      'Run "pip install pymongo" to install it.')

from .base_observer import ExperimentObserver


class PickleNumpyArrays(SONManipulator):
    def transform_incoming(self, son, collection):
        for (key, value) in son.items():
            if isinstance(value, np.ndarray):
                son[key] = {"_type": "ndarray",
                            "_value": Binary(cPickle.dumps(value, protocol=2))}
            elif isinstance(value, dict):  # Make sure we recurse into sub-docs
                son[key] = self.transform_incoming(value, collection)
        return son

    def transform_outgoing(self, son, collection):
        for (key, value) in son.items():
            if isinstance(value, dict):
                if "_type" in value and value["_type"] == "ndarray":
                    son[key] = cPickle.loads(str(value["_value"]))
                else:  # Again, make sure to recurse into sub-docs
                    son[key] = self.transform_outgoing(value, collection)
        return son


class MongoDBReporter(ExperimentObserver):
    def __init__(self, url=None, db_name='mlizard_experiments', save_delay=1):
        super(MongoDBReporter, self).__init__()
        self.experiment_skeleton = dict()
        self.experiment_entry = dict()
        self.last_save = 0
        self.save_delay = save_delay
        mongo = MongoClient(url)
        self.db = mongo[db_name]
        self.db.add_son_manipulator(PickleNumpyArrays())
        self.collection = self.db['experiments']

    def save(self):
        self.last_save = time.time()
        self.collection.save(self.experiment_entry)

    def experiment_created_event(self, name, stages, seed, mainfile, doc):
        self.experiment_skeleton['name'] = name
        self.experiment_skeleton['stages'] = [s.__name__ for s in stages]
        self.experiment_skeleton['mainfile'] = mainfile
        self.experiment_skeleton['doc'] = doc

    def experiment_started_event(self, start_time, options, run_seed, args,
                                 kwargs, info):
        # when an experiment starts, always make a new db entry
        # so we can rerun the same experiment and get multiple entries
        self.experiment_entry = deepcopy(self.experiment_skeleton)

        self.experiment_entry['start_time'] = start_time
        self.experiment_entry['options'] = options
        self.experiment_entry['seed'] = run_seed
        self.experiment_entry['args'] = args
        self.experiment_entry['kwargs'] = kwargs
        self.experiment_entry['info'] = info
        self.experiment_entry['status'] = 'RUNNING'
        self.save()

    def experiment_info_updated(self, info):
        self.experiment_entry['info'] = info
        if time.time() >= self.last_save + self.save_delay:
            self.save()

    def experiment_completed_event(self, stop_time, result, info):
        self.experiment_entry['stop_time'] = stop_time
        self.experiment_entry['result'] = result
        self.experiment_entry['info'] = info
        self.experiment_entry['status'] = 'COMPLETED'
        self.save()

    def experiment_interrupted_event(self, interrupt_time, info):
        self.experiment_entry['stop_time'] = interrupt_time
        self.experiment_entry['info'] = info
        self.experiment_entry['status'] = 'INTERRUPTED'
        self.save()

    def experiment_failed_event(self, fail_time, info):
        self.experiment_entry['stop_time'] = fail_time
        self.experiment_entry['info'] = info
        self.experiment_entry['status'] = 'FAILED'
        self.save()
