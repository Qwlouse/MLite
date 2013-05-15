#!/usr/bin/python
# coding=utf-8

from __future__ import division, print_function, unicode_literals


class ExperimentObserver(object):
    def experiment_created_event(self, name, stages, seed, mainfile, doc):
        pass

    def experiment_started_event(self, start_time, options, run_seed, args, kwargs):
        pass

    def experiment_completed_event(self, stop_time, result):
        pass


class CouchDBReporter(ExperimentObserver):
    def __init__(self, url=None, db_name='mlizard_experiments'):
        super(CouchDBReporter, self).__init__()
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
        self.experiment_entry['name'] = name
        self.experiment_entry['stages'] = [s.__name__ for s in stages]
        self.experiment_entry['mainfile'] = mainfile
        self.experiment_entry['doc'] = doc
        self.save()

    def experiment_started_event(self, start_time, options, run_seed, args, kwargs):
        self.experiment_entry['start_time'] = start_time
        self.experiment_entry['options'] = options
        self.experiment_entry['seed'] = run_seed
        self.experiment_entry['args'] = args
        self.experiment_entry['kwargs'] = kwargs
        self.save()

    def experiment_completed_event(self, stop_time, result):
        self.experiment_entry['stop_time'] = stop_time
        self.experiment_entry['result'] = result
        self.save()
