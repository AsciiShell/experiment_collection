import abc
import datetime

import typing


class StorageABC(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def close(self):
        """close database connection"""

    @abc.abstractmethod
    def check_permission(self, token: str, namespace: str) -> bool:
        """check if token have permission for namespace"""

    @abc.abstractmethod
    def reserve_experiment(self, namespace: str, name: str, duration: int) -> bool:
        """reserve experiment for duration seconds

        You can mark some experiment as 'started', so other workers will not process same experiment
        """

    # pylint: disable=R0913
    @abc.abstractmethod
    def create_experiment(self, namespace: str, name: str, params: str, metrics: str, time: datetime.datetime) -> bool:
        """add experiment to collection"""

    @abc.abstractmethod
    def delete_experiment(self, namespace: str, name: str):
        """delete experiment from collection"""

    @abc.abstractmethod
    def check_experiment(self, namespace: str, name: str) -> bool:
        """return True if experiment exists (created or reserved"""

    @abc.abstractmethod
    def get_experiments(self, namespace: str) -> typing.List[typing.Dict]:
        """return all experiments from namespace"""

    @abc.abstractmethod
    def revoke_token(self, token: str):
        """remove all permission for token"""

    @abc.abstractmethod
    def create_token(self, token: str) -> bool:
        """create new empty token"""

    @abc.abstractmethod
    def grant_permission(self, token: str, namespace: str) -> bool:
        """add permission to namespace"""
