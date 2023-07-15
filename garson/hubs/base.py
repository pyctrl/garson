import abc

from garson.services import base


class AbstractHub(base.AbstractService):

    @abc.abstractmethod
    def add_target(self):
        raise NotImplementedError


class AbstractSyncHub(AbstractHub):

    @abc.abstractmethod
    def call_target(self):
        raise NotImplementedError


class AbstractAsyncHub(AbstractHub):

    @abc.abstractmethod
    def spawn_target(self):
        raise NotImplementedError

    @abc.abstractmethod
    def check_target(self):
        raise NotImplementedError
