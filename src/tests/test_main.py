import random
import string

import pytest
import time

import experiment_collection
from experiment_collection_server.__main__ import serve


class TestCollection:
    def setup_class(cls):
        cls.server, cls.servicer = serve(False)
        namespace = 'main_' + ''.join(random.choices(string.ascii_letters, k=4))
        token = ''.join(random.choices(string.ascii_letters, k=16))
        cls.servicer.db.create_token(token)
        cls.servicer.db.grant_permission(token, namespace)
        cls.coll = experiment_collection.ExperimentCollectionRemote('localhost:50051', namespace, token)

    def teardown_class(cls):
        for index, row in cls.coll.get_experiments().iterrows():
            exp = row['name']
            cls.coll.delete_experiment(exp)
        cls.coll.revoke(force=True)
        cls.coll.close()

    def test_reserve(self):
        exp = experiment_collection.Experiment('test_reserve', params={'lr': 0.1}, metrics={'auc': 0.7})
        assert self.coll.reserve_experiment(exp, 3)
        assert not self.coll.reserve_experiment(exp, 3)
        assert self.coll.check_experiment(exp)
        time.sleep(5)
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
