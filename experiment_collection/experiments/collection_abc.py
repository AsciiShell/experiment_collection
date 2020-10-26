import abc
import typing

from .experiment import Experiment


class ExperimentCollectionABC(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def close(self):
        pass

    @abc.abstractmethod
    def add_experiment(self, exp: Experiment, /, ignore_included=False):
        pass

    @abc.abstractmethod
    def delete_experiment(self, exp: typing.Union[Experiment, str]):
        pass

    @abc.abstractmethod
    def check_experiment(self, exp: typing.Union[Experiment, str]) -> bool:
        pass

    @abc.abstractmethod
    def get_experiments(self, normalize=True):
        pass
