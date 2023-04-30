from __future__ import annotations

import logging
import time

from garson.schedulers import base as sched
from garson.services import base


LOG = logging.getLogger(__name__)


class Steps:

    _MIN_STUB = sched.FakeScheduler().schedule()

    def __init__(self, *steps: sched.AbstractScheduler):
        self._base_index = 0
        self._steps = steps
        self.next = self._next_single if len(steps) == 1 else self._next_multi

    def _next_single(self) -> sched.Schedule:
        return self._steps[0].schedule()

    def _next_multi(self) -> sched.Schedule:
        steps_count = len(self._steps)
        base_index, result = self._base_index, self._MIN_STUB
        for i in range(steps_count):
            index = (self._base_index + i) % steps_count
            step = self._steps[index]
            schedule = step.schedule()
            if schedule.is_ready():
                self._base_index = (index + 1) % steps_count
                return schedule
            if schedule.delay < result.delay:
                base_index, result = (index + 1) % steps_count, schedule
        self._base_index = base_index
        return result


class StepService(base.AbstractService):

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
        self._steps = Steps(scheduled_step, *scheduled_steps)

    def _setup(self):
        super()._setup()
        self._loop = True

    def _step(self, schedule):
        LOG.debug(">> Starting step '%s' with iteration=%d",
                  schedule.scheduler.name, schedule.iteration)
        try:
            # or scheduler?  # + step info
            schedule.scheduler.run(args=(self, schedule))
        except Exception as e:
            LOG.exception("<< [!!] Step '%s' with iteration=%d has failed: %s",
                          schedule.scheduler.name, schedule.iteration, e)
        else:
            LOG.debug("<< Step '%s' with iteration=%d successfully finished",
                      schedule.scheduler.name, schedule.iteration)

    def _serve(self):
        while self._loop:
            schedule = self._steps.next()
            if schedule.is_ready():
                self._step(schedule)
            else:
                LOG.debug("Sleeping: %s", schedule.delay)
                time.sleep(min(schedule.delay, self._max_sleep))

    def _stop(self):
        self._loop = False

    def _check_alive(self) -> None:
        return
