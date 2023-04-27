from __future__ import annotations

import abc
import logging
import time
import typing as t

from garson.schedulers import base as sched
from garson.services import base


LOG = logging.getLogger(__name__)


class AbstractStep(abc.ABC):

    def __init__(self, scheduler: sched.AbstractScheduler):
        self.scheduler = scheduler

    @abc.abstractmethod
    def __call__(self):
        raise NotImplementedError


class StepService(base.AbstractService):

    _next_step: t.Optional[AbstractStep]

    def __init__(self,
                 step: AbstractStep,
                 *steps: AbstractStep,
                 operate: bool = True,
                 contexts=None,
                 daemonize: bool = True):
        super().__init__(operate=operate,
                         contexts=contexts,
                         daemonize=daemonize)
        self._loop = False
        self._steps = (step, *steps)
        if steps:
            self._single_step = False
            self._next_step = None
        else:
            self._single_step = True
            self._next_step = self._steps[0]

    def _setup(self):
        super()._setup()
        self._loop = True

    def _schedule(self):
        if self._single_step:
            return self._next_step.scheduler.schedule()[0], self._next_step

        if self._next_step:
            delay = self._next_step.scheduler.schedule()[0]
            next_step = self._next_step
        else:
            delay, _, _, next_step = sorted(
                (*step.scheduler.schedule(), step) for step in self._steps
            )[0]

        if delay <= 0:
            self._next_step = None

        return delay, next_step

    def _serve(self):
        while self._loop:
            delay, step = self._schedule()

            if delay > 0:
                time.sleep(delay)
                continue

            try:
                step()
                LOG.debug("Step finished successfully")
            except Exception as e:
                LOG.exception("Step failed: %s", e)

    def _stop(self):
        self._loop = False
