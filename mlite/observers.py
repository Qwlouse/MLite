#!/usr/bin/python
# coding=utf-8

from __future__ import division, print_function, unicode_literals
from copy import deepcopy


class ExperimentObserver(object):
    def experiment_created_event(self, name, stages, seed, mainfile, doc):
        pass

    def experiment_started_event(self, start_time, options, run_seed, args,
                                 kwargs, info):
        pass

    def experiment_completed_event(self, stop_time, result, info):
        pass


class CouchDBReporter(ExperimentObserver):
    def __init__(self, url=None, db_name='mlizard_experiments'):
        super(CouchDBReporter, self).__init__()
        self.experiment_skeleton = dict()
        self.experiment_entry = dict()
        try:
            import couchdb
            couch = couchdb.Server(url) if url else couchdb.Server()
            if db_name in couch:
                self.db = couch[db_name]
            else:
                self.db = couch.create(db_name)
        except ImportError:
            raise ImportError('This Observer depends on the couchdb python '
                              'package. Run pip install CouchDB to install it.')

    def save(self):
        self.db.save(self.experiment_entry)

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
        self.save()

    def experiment_completed_event(self, stop_time, result, info):
        self.experiment_entry['stop_time'] = stop_time
        self.experiment_entry['result'] = result
        self.experiment_entry['info'] = info
        self.save()
