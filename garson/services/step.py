from __future__ import annotations

import logging
import time
import typing as t

from garson.schedulers import base as sched
from garson.services import base


LOG = logging.getLogger(__name__)


def _get_next_step(steps: t.Iterable[sched.AbstractScheduler]):
    steps = iter(steps)
    result = next(steps).schedule()
    if result.is_ready():
        return result
    for step in steps:
        schedule = step.schedule()
        if schedule.is_ready():
            return schedule
        result = min(result, schedule)
    return result


class StepService(base.AbstractService):

    _next_step: t.Optional[sched.AbstractScheduler]

    def __init__(self,
                 scheduled_step: sched.AbstractScheduler,
                 *scheduled_steps: sched.AbstractScheduler,
                 responsiveness_period: int | float = 1,
                 operate: bool = True,
                 contexts=None,
                 daemonize: bool = True):
        super().__init__(operate=operate,
                         contexts=contexts,
                         daemonize=daemonize)
        self._max_sleep = responsiveness_period
        self._loop = False
        self._steps = [scheduled_step, *scheduled_steps]
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
            schedule = _get_next_step(self._steps)

        if schedule.delay <= 0:
            self._next_step = None

        return schedule

    def _serve(self):
        while self._loop:
            schedule = self._schedule()

            if not schedule.is_ready():
                LOG.debug("Sleeping: %s", schedule.delay)
                time.sleep(min(schedule.delay, self._max_sleep))
                continue

            LOG.debug(">> Starting step with iteration=%d",
                      schedule.iteration)
            try:
                schedule.run(self, schedule)  # or scheduler?  # + step info
            except Exception as e:
                LOG.exception("<< [!!] Step with iteration=%d has failed: %s",
                              e)
            else:
                LOG.debug("<< Step with iteration=%d successfully finished",
                          schedule.iteration)

    def _stop(self):
        self._loop = False

    def _check_alive(self) -> None:
        return
