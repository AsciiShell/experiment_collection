import datetime
import logging
from functools import wraps

import time
from google.protobuf.empty_pb2 import Empty
from google.protobuf.timestamp_pb2 import Timestamp

from experiment_collection_core import service_pb2, service_pb2_grpc
from experiment_collection_server.db.storage_abc import StorageABC

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def catch_exceptions(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start = time.time()
        try:
            result = f(*args, **kwargs)
        except Exception:
            logger.exception('%.4fms %s from %s', 1000 * (time.time() - start), f.__name__, args[2].peer())
            return Empty()
        logger.info('%.4fms %s from %s', 1000 * (time.time() - start), f.__name__, args[2].peer())
        return result

    return decorated_function


class Servicer(service_pb2_grpc.ExperimentServiceServicer):
    def __init__(self, storage: StorageABC):
        self.db = storage

    # pylint: disable=W0613
    def check_permission(self, request, context):
        try:
            return self.db.check_permission(request.token, request.namespace)
        except Exception:
            logger.exception('cannot check permission')
            return False

    @catch_exceptions
    def CreateExperiment(self, request, context):
        if not self.check_permission(request, context):
            return service_pb2.SimpleReply(status=False, error='access denied')
        exp = request.experiment
        ts = datetime.datetime.fromtimestamp(exp.time.seconds + exp.time.nanos / 1e9)
        if self.db.create_experiment(request.namespace, exp.name, exp.params, exp.metrics, ts):
            return service_pb2.SimpleReply(status=True)
        return service_pb2.SimpleReply(status=False, error='cannot add experiment')

    @catch_exceptions
    def ReserveExperiment(self, request, context):
        if not self.check_permission(request, context):
            return service_pb2.SimpleReply(status=False, error='access denied')
        if self.db.reserve_experiment(request.namespace, request.experiment, request.duration):
            return service_pb2.SimpleReply(status=True)
        return service_pb2.SimpleReply(status=False, error='experiment exists')

    @catch_exceptions
    def DeleteExperiment(self, request, context):
        if not self.check_permission(request, context):
            return service_pb2.SimpleReply(status=False, error='access denied')
        self.db.delete_experiment(request.namespace, request.experiment)
        return service_pb2.SimpleReply(status=True)

    @catch_exceptions
    def CheckExperiment(self, request, context):
        if not self.check_permission(request, context):
            return service_pb2.SimpleReply(status=False, error='access denied')
        status = self.db.check_experiment(request.namespace, request.experiment)
        return service_pb2.SimpleReply(status=status)

    @catch_exceptions
    def GetExperiments(self, request, context):
        if not self.check_permission(request, context):
            return service_pb2.SimpleReply(status=False, error='access denied')
        resp = service_pb2.ExperimentsReply(status=True)
        for name, params, metrics, ts in self.db.get_experiments(request.namespace):
            tspb = Timestamp()
            # pylint: disable=E1101
            tspb.FromDatetime(ts)
            # pylint: disable=E1101
            resp.experiments.append(
                service_pb2.Experiment(name=name, time=tspb, params=params, metrics=metrics))
        return resp

    @catch_exceptions
    def CreateNamespace(self, request, context):
        self.db.grant_permission(request.token, request.namespace)
        return service_pb2.SimpleReply(status=True)

    @catch_exceptions
    def RevokeToken(self, request, context):
        self.db.revoke_token(request.token)
        return service_pb2.SimpleReply(status=True)

    @catch_exceptions
    def GrantAccess(self, request, context):
        if not self.check_permission(request, context):
            return service_pb2.SimpleReply(status=False, error='access denied')
        self.db.grant_permission(request.other_token, request.namespace)
        return service_pb2.SimpleReply(status=True)
