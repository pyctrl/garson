from __future__ import annotations

import logging
import operator
import time
import typing as t

from garson.schedulers import base as sched
from garson.services import base


LOG = logging.getLogger(__name__)


class StepService(base.AbstractService):

    _next_step: t.Optional[sched.AbstractScheduler]

    def __init__(self,
                 scheduled_step: sched.AbstractScheduler,
                 *scheduled_steps: sched.AbstractScheduler,
                 operate: bool = True,
                 contexts=None,
                 daemonize: bool = True):
        super().__init__(operate=operate,
                         contexts=contexts,
                         daemonize=daemonize)
        self._loop = False
        self._steps = (scheduled_step, *scheduled_steps)
        if scheduled_steps:
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
            return self._next_step.schedule()

        if self._next_step:
            schedule = self._next_step.schedule()
        else:
            schedule = sorted((step.schedule() for step in self._steps),
                              key=operator.attrgetter(sched._F_DELAY))

        if schedule.delay <= 0:
            self._next_step = None

        return schedule

    def _serve(self):
        while self._loop:
            schedule = self._schedule()

            if schedule.delay > 0:
                LOG.debug("Sleeping: %s", schedule.delay)
                time.sleep(schedule.delay)
                continue

            try:
                LOG.debug(">> Starting step/iterations")
                schedule.target(self, schedule)  # or scheduler?  # + step info
                LOG.debug("<< Step finished successfully")
            except Exception as e:
                LOG.exception("<< [!!] Step failed: %s", e)

    def _stop(self):
        self._loop = False
