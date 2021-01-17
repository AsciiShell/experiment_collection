import argparse
import logging
import os
from concurrent import futures

import grpc
from configargparse import ArgumentParser
# pylint: disable=E0611
from setproctitle import setproctitle

from experiment_collection_core import service_pb2_grpc
from experiment_collection_server.db.storage_postgresql import StoragePostgresql
from experiment_collection_server.db.storage_sqlite import StorageSQLite
from experiment_collection_server.service import Servicer

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

ENV_VAR_PREFIX = 'EXPERIMENT_'

parser = ArgumentParser(
    auto_env_var_prefix=ENV_VAR_PREFIX, allow_abbrev=False,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
group = parser.add_argument_group('Storage Options')
group.add_argument('--storage-type', type=str, help='Storage type (sqlite/postgres)')
group.add_argument('--sqlite-path', type=str, help='sqlite database path')
group.add_argument('--postgres-dsn', type=str, help='postgres connection string')
group = parser.add_argument_group('Server Options')
group.add_argument('--workers', type=int, default=1, help='Number of workers')
group.add_argument('--port', type=str, help='server port')
group = parser.add_argument_group('Token Options')
group.add_argument('--token', type=str, help='Token to create')
parser.add_argument('--action', type=str, help='Type of task (run/token)')


def _get_storage(args):
    if args.storage_type == 'sqlite':
        return StorageSQLite(args.sqlite_path)
    if args.storage_type == 'postgres':
        return StoragePostgresql(args.postgres_dsn)
    raise Exception('Unknown storage type "{}"'.format(args.storage_type))


def main_server(args):
    storage = _get_storage(args)
    servicer = Servicer(storage)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=args.workers))
    service_pb2_grpc.add_ExperimentServiceServicer_to_server(servicer, server)
    server.add_insecure_port(args.port)
    server.start()
    logger.info('start server')
    server.wait_for_termination()


def main_token(args):
    storage = _get_storage(args)
    if storage.create_token(args.token):
        logger.info('Token created')
    else:
        logger.error('Cannot add token')


def main():
    args = parser.parse_args()
    for name in filter(lambda x: x.startswith(ENV_VAR_PREFIX), tuple(os.environ)):
        os.environ.pop(name)
    setproctitle('experiment_collection')
    if args.action == 'run':
        main_server(args)
    elif args.action == 'token':
        main_token(args)
    else:
        print(parser.format_help())


if __name__ == '__main__':
    main()
