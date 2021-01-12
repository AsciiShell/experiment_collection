import datetime
import logging
from concurrent import futures

import grpc
from google.protobuf.timestamp_pb2 import Timestamp

from experiment_collection_core import service_pb2, service_pb2_grpc
from experiment_collection_server.db.storage_sqlite import StorageSQLite

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


class Servicer(service_pb2_grpc.ExperimentServiceServicer):
    def __init__(self):
        self.db = StorageSQLite()

    def check_permission(self, request, context):
        return self.db.check_permission(request.token, request.namespace)

    def CreateExperiment(self, request, context):
        if not self.check_permission(request, context):
            return service_pb2.SimpleReply(status=False, error='access denied')
        exp = request.experiment
        ts = datetime.datetime.fromtimestamp(exp.time.seconds + exp.time.nanos / 1e9)
        self.db.create_experiment(request.namespace, exp.name, exp.params, exp.metrics, ts)
        return service_pb2.SimpleReply(status=True)

    def ReserveExperiment(self, request, context):
        if not self.check_permission(request, context):
            return service_pb2.SimpleReply(status=False, error='access denied')
        if self.db.reserve_experiment(request.namespace, request.experiment, request.duration):
            return service_pb2.SimpleReply(status=True)
        return service_pb2.SimpleReply(status=False, error='experiment exists')

    def DeleteExperiment(self, request, context):
        if not self.check_permission(request, context):
            return service_pb2.SimpleReply(status=False, error='access denied')
        self.db.delete_experiment(request.namespace, request.experiment)
        return service_pb2.SimpleReply(status=True)

    def CheckExperiment(self, request, context):
        if not self.check_permission(request, context):
            return service_pb2.SimpleReply(status=False, error='access denied')
        status = self.db.check_experiment(request.namespace, request.experiment)
        return service_pb2.SimpleReply(status=status)

    def GetExperiments(self, request, context):
        if not self.check_permission(request, context):
            return service_pb2.SimpleReply(status=False, error='access denied')
        resp = service_pb2.ExperimentsReply(status=True)
        for exp in self.db.get_experiments(request.namespace):
            ts = Timestamp()
            ts.FromDatetime(datetime.datetime.strptime(exp[3], '%Y-%m-%d %H:%M:%S.%f'))
            resp.experiments.append(
                service_pb2.Experiment(name=exp[0], time=ts, params=exp[1], metrics=exp[2]))
        return resp

    def CreateNamespace(self, request, context):
        self.db.create_namespace(request.token, request.namespace)
        return service_pb2.SimpleReply(status=True)

    def DeleteNamespace(self, request, context):
        if not self.check_permission(request, context):
            return service_pb2.SimpleReply(status=False, error='access denied')
        self.db.delete_namespace(request.namespace)
        return service_pb2.SimpleReply(status=True)

    def RevokeToken(self, request, context):
        self.db.revoke_token(request.token)
        return service_pb2.SimpleReply(status=True)

    def GrantAccess(self, request, context):
        if not self.check_permission(request, context):
            return service_pb2.SimpleReply(status=False, error='access denied')
        self.db.grant_permission(request.other_token, request.namespace)
        return service_pb2.SimpleReply(status=True)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    service_pb2_grpc.add_ExperimentServiceServicer_to_server(Servicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    logger.info('start server')
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
