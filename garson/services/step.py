from __future__ import annotations

import abc
import logging
import time

from garson.schedulers import base as sched
from garson.services import base


logging.basicConfig(level=logging.DEBUG)  # TODO(d.burmistrov): dev only
LOG = logging.getLogger(__name__)


class StepService(base.AbstractService):

    def __init__(self,
                 scheduler: sched.AbstractScheduler,
                 operate: bool = True,
                 contexts=None,
                 daemonize: bool = True):
        super().__init__(operate=operate,
                         contexts=contexts,
                         daemonize=daemonize)
        self._sched = scheduler
        self._loop = False

    def _setup(self):
        super()._setup()
        self._loop = True

    def _serve(self):
        while self._loop:
            now, next_launch = self._sched.schedule()
            if now < next_launch:
                time.sleep(next_launch - now)
                continue

            try:
                self._step(scheduler=self._sched)
                LOG.debug("Step finished successfully")
            except Exception as e:
                LOG.exception("Step failed: %s", e)

    def _stop(self):
        self._loop = False

    @abc.abstractmethod
    def _step(self, scheduler: sched.AbstractScheduler):
        raise NotImplementedError()
