import random
import string
import time
from concurrent import futures

import grpc
import pytest

import experiment_collection
from experiment_collection_core import service_pb2_grpc
from experiment_collection_server.db.storage_sqlite import StorageSQLite
from experiment_collection_server.service import Servicer


class TestCollection:
    db = None
    server = None
    coll = None

    def setup_class(self):
        self.db = StorageSQLite()
        servicer = Servicer(self.db)
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
        service_pb2_grpc.add_ExperimentServiceServicer_to_server(servicer, self.server)
        self.server.add_insecure_port('[::]:50051')
        self.server.start()
        namespace = 'main_' + ''.join(random.choices(string.ascii_letters, k=4))
        token = ''.join(random.choices(string.ascii_letters, k=16))
        self.db.create_token(token)
        self.db.grant_permission(token, namespace)
        self.coll = experiment_collection.ExperimentCollectionRemote('localhost:50051', namespace, token)

    def teardown_class(self):
        for _, row in self.coll.get_experiments().iterrows():
            exp = row['name']
            self.coll.delete_experiment(exp)
        self.coll.revoke(force=True)
        self.coll.close()
        self.server.stop(False)
        self.db.close()

    def test_reserve(self):
        exp = experiment_collection.Experiment('test_reserve', params={'lr': 0.1}, metrics={'auc': 0.7})
        assert self.coll.reserve_experiment(exp, 1)
        assert not self.coll.reserve_experiment(exp, 1)
        assert self.coll.check_experiment(exp)
        time.sleep(2)
        assert not self.coll.check_experiment(exp)

    def test_add(self):
        exp = experiment_collection.Experiment('test_add', params={'lr': 0.1}, metrics={'auc': 0.7})
        assert not self.coll.check_experiment(exp)
        self.coll.add_experiment(exp)
        with pytest.raises(experiment_collection.collection_remote.ExperimentCollectionRemoteException):
            self.coll.add_experiment(exp)
        self.coll.add_experiment(exp, ignore_included=True)
        assert self.coll.check_experiment(exp)

        self.coll.delete_experiment(exp)
        self.coll.delete_experiment(exp)
        assert not self.coll.check_experiment(exp)
