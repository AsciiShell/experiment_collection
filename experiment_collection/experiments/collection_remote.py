import json
import typing
import urllib.parse

import pandas as pd
import requests

from .collection_abc import ExperimentCollectionABC
from .experiment import Experiment
from .utils import postprocess_df

INSERT_URL = 'experiment'
SELECT_EXISTS_URL = INSERT_URL
DELETE_URL = INSERT_URL
SELECT_URL = 'all_experiments'


class ExperimentCollectionRemoteException(Exception):
    pass


class ExperimentCollectionRemote(ExperimentCollectionABC):
    def __init__(self, host, collection_name):
        self.host = host
        self.collection_name = collection_name

    def close(self):
        pass

    def add_experiment(self, exp: Experiment, /, ignore_included=False):
        data = exp.dumps_json()
        data['collection_name'] = self.collection_name
        url = urllib.parse.urljoin(self.host, INSERT_URL)
        r = requests.post(url, data=data)
        if not r.ok and not ignore_included and self.check_experiment(exp):
            raise ExperimentCollectionRemoteException(r.text)

    def delete_experiment(self, exp: typing.Union[Experiment, str]):
        if isinstance(exp, Experiment):
            exp = exp.name
        data = {'collection_name': self.collection_name, 'name': exp}
        url = urllib.parse.urljoin(self.host, DELETE_URL)
        r = requests.delete(url, data=data)
        if not r.ok:
            raise ExperimentCollectionRemoteException(r.text)

    def check_experiment(self, exp: typing.Union[Experiment, str]) -> bool:
        if isinstance(exp, Experiment):
            exp = exp.name
        data = {'collection_name': self.collection_name, 'name': exp}
        url = urllib.parse.urljoin(self.host, SELECT_EXISTS_URL)
        r = requests.get(url, data=data)
        if not r.ok:
            raise ExperimentCollectionRemoteException(r.text)
        return json.loads(r.text)

    def get_experiments(self, normalize=True):
        data = {'collection_name': self.collection_name}
        url = urllib.parse.urljoin(self.host, SELECT_URL)
        r = requests.post(url, data=data)
        if not r.ok:
            raise ExperimentCollectionRemoteException(r.text)
        js = json.loads(r.text)

        df = pd.DataFrame(js, columns=['name', 'params', 'metrics', 'time'])
        df = postprocess_df(df, normalize)
        return df
