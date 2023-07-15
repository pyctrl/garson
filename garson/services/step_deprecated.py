from __future__ import annotations

import abc
import logging
import time

from garson.schedulers import base as sched
from garson.services import base


LOG = logging.getLogger(__name__)


class StepService(base.AbstractService):

    def __init__(self,
                 scheduler: sched.SchedulerInterface,
                 contexts=None,
                 daemonize: bool = True):
        super().__init__(contexts=contexts,
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
                self._l(LOG).debug("Step finished successfully")
            except Exception as e:
                self._l(LOG).exception("Step failed: %s", e)

    def _stop(self):
        self._loop = False

    @abc.abstractmethod
    def _step(self, scheduler: sched.SchedulerInterface):
        raise NotImplementedError()
