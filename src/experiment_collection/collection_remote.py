import datetime
import json
import typing

import grpc
import pandas as pd
from google.protobuf.timestamp_pb2 import Timestamp

from experiment_collection.utils import postprocess_df
from experiment_collection_core import service_pb2_grpc, service_pb2
from .collection_abc import ExperimentCollectionABC
from .experiment import Experiment


class ExperimentCollectionRemoteException(Exception):
    pass


class ExperimentCollectionRemote(ExperimentCollectionABC):
    def __init__(self, host: str, namespace: str, token: str, credentials=None):
        self._credentials = credentials
        self._host = host
        self._namespace = namespace
        self._token = token
        if credentials is None:
            self.channel = grpc.insecure_channel(host)
        else:
            if isinstance(credentials, bool) and credentials:
                credentials = grpc.ssl_channel_credentials()
            self.channel = grpc.secure_channel(host, credentials)
        self.stub = service_pb2_grpc.ExperimentServiceStub(self.channel)
        self.auth = {'namespace': self._namespace, 'token': self._token}

    def close(self):
        self.channel.close()

    def add_experiment(self, exp: Experiment, *, ignore_included=False):
        ts = Timestamp()
        # pylint: disable=E1101
        ts.FromDatetime(exp.time)
        experiment = service_pb2.Experiment(name=exp.name,
                                            params=json.dumps(exp.params),
                                            metrics=json.dumps(exp.metrics),
                                            time=ts,
                                            )
        r = self.stub.CreateExperiment(service_pb2.AddExperiment(experiment=experiment, **self.auth))
        if not r.status and not ignore_included and self.check_experiment(exp):
            raise ExperimentCollectionRemoteException(r.error)

    def reserve_experiment(self, exp: typing.Union[Experiment, str], duration: int) -> bool:
        assert duration > 0, 'Duration should be more than zero'
        if isinstance(exp, Experiment):
            exp = exp.name
        r = self.stub.ReserveExperiment(
            service_pb2.ReserveExperimentRequest(experiment=exp, duration=duration, **self.auth))
        return r.status

    def delete_experiment(self, exp: typing.Union[Experiment, str]):
        if isinstance(exp, Experiment):
            exp = exp.name
        r = self.stub.DeleteExperiment(service_pb2.SimpleExperiment(experiment=exp, **self.auth))
        if not r.status:
            raise ExperimentCollectionRemoteException(r.error)

    def check_experiment(self, exp: typing.Union[Experiment, str]) -> bool:
        if isinstance(exp, Experiment):
            exp = exp.name
        r = self.stub.CheckExperiment(service_pb2.SimpleExperiment(experiment=exp, **self.auth))
        return r.status

    def get_experiments(self, normalize=True):
        r = self.stub.GetExperiments(service_pb2.SimpleNamespace(**self.auth))
        if not r.status:
            raise ExperimentCollectionRemoteException(r.error)
        experiments = {'name': [], 'params': [], 'metrics': [], 'time': []}
        for exp in r.experiments:
            ts = datetime.datetime.fromtimestamp(exp.time.seconds + exp.time.nanos / 1e9)
            experiments['name'].append(exp.name)
            experiments['params'].append(exp.params)
            experiments['metrics'].append(exp.metrics)
            experiments['time'].append(ts)
        df = pd.DataFrame(experiments)
        df = postprocess_df(df, normalize)
        return df

    def create_namespace(self, name: str):
        r = self.stub.CreateNamespace(service_pb2.SimpleNamespace(namespace=name, token=self._token))
        if r.status:
            return ExperimentCollectionRemote(self._host, name, self._token, self._credentials)
        raise ExperimentCollectionRemoteException(r.error)

    def revoke(self, *, force=False):
        if force or input('enter YES to revoke access to all your namespaces') == 'YES':
            r = self.stub.RevokeToken(service_pb2.SimpleToken(token=self._token))
            if not r.status:
                raise ExperimentCollectionRemoteException(r.error)
        else:
            raise ExperimentCollectionRemoteException('abort')

    def grant(self, token: str):
        r = self.stub.GrantAccess(service_pb2.GrantAccessRequest(other_token=token, **self.auth))
        if not r.status:
            raise ExperimentCollectionRemoteException(r.error)
