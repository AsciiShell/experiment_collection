import datetime
import json

from .utils import prepare_dict


class Experiment:
    def __init__(self, name, params=None, metrics=None):
        self.params = {}
        self.metrics = {}
        self.name = name
        self.set_params({} if params is None else params)
        self.set_metrics({} if metrics is None else metrics)
        self.time = datetime.datetime.now()

    def set_params(self, params):
        self.params = prepare_dict(params)

    def set_metrics(self, metrics):
        self.metrics = prepare_dict(metrics)

    def dumps_dict(self):
        return {
            'name': self.name,
            'params': json.dumps(self.params),
            'metrics': json.dumps(self.metrics),
            'time': self.time,
        }
