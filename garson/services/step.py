import abc
import logging
import time

from garson.services import base


logging.basicConfig(level=logging.DEBUG)  # TODO(d.burmistrov): dev only
LOG = logging.getLogger(__name__)


class Controller:
    def __init__(self, svc):
        self._svc = svc

    def step(self):
        self._svc._step()
        return 0.5


class StepService(base.AbstractService):

    def __init__(self, operate=True, contexts=None, daemonize=True):
        super().__init__(operate=operate,
                         contexts=contexts,
                         daemonize=daemonize)
        self._ctrl = Controller(self)
        self._loop = False

    def _setup(self):
        super()._setup()
        self._loop = True

    def _serve(self):
        while self._loop:
            if delay := self._ctrl.step():
                time.sleep(delay)

    def _stop(self):
        self._loop = False

    @abc.abstractmethod
    def _step(self):
        raise NotImplementedError()


class S(StepService):

    def _step(self):
        LOG.info("My service >> step <<")


if __name__ == "__main__":
    S().serve()
