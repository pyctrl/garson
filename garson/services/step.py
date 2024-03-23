from __future__ import annotations

import abc
import logging
import time
import typing as t

from garson._lib import info as i
from garson._lib import utils
from garson.schedulers import base as sched
from garson.services import base


LOG = logging.getLogger(__name__)


def _strategy_single(step):
    while True:
        yield step, step.schedule()


def _strategy_multi_1(*steps):
    base_index = 0
    steps_count = len(steps)
    while True:
        step = steps[base_index]
        result = step.schedule()
        for j in range(1, steps_count):
            index = (base_index + j) % steps_count
            candidate = steps[index]
            appt = candidate.schedule()
            delay = appt.delay
            if delay <= 0:
                base_index = (index + 1) % steps_count
                result = appt
                step = candidate
                break
            if delay < result.delay:
                base_index = (index + 1) % steps_count
                result = appt
        yield step, result


class AbstractStep(abc.ABC):

    def __init__(self,
                 scheduler: sched.SchedulerInterface,
                 name: t.Optional[str] = None):
        self.name = name or type(self).__name__
        self._scheduler = scheduler
        self.service: t.Optional[StepService] = None
        self._iteration = 1
        self.info = i.Info()
        self._reset_info()

    def _l(self, logger):
        return logger

    def _reset_info(self):
        self.info.do_clear()
        self.info.do_update(name=self.name, iteration=self._iteration)

    def __call__(self):
        self._reset_info()
        self._l(LOG).debug(
            ">> Starting step '%s' with iteration=%d",
            self.name, self._iteration,
        )
        try:
            with utils.measure(self.info):
                self._step()
            self._l(LOG).debug(
                "<< Step '%s' with iteration=%d successfully finished",
                self.name, self._iteration,
            )
        except Exception as e:
            self._l(LOG).exception(
                "<< [!!] Step '%s' with iteration=%d has failed: %s",
                self.name, self._iteration, e,
            )
        finally:
            self._iteration += 1

    def schedule(self) -> sched.Appointment:
        return self._scheduler.schedule()

    def attach_service(self, service: StepService) -> None:
        self.service = service

    @abc.abstractmethod
    def _step(self):
        raise NotImplementedError


class StepService(base.AbstractService):

    SERVICE_TYPE = "step"

    _STRATEGIES = (_strategy_single, _strategy_multi_1)

    def __init__(self,
                 step: AbstractStep,
                 *steps: AbstractStep,
                 responsiveness_period: int | float = 1,
                 contexts=None,
                 daemonize: bool = True):
        # TODO(d.burmistrov): allow strategy as parameter
        super().__init__(contexts=contexts,
                         daemonize=daemonize)
        self._max_sleep = responsiveness_period
        self._loop = False
        step.attach_service(self)
        for s in steps:
            s.attach_service(self)
        self._steps = self._STRATEGIES[bool(steps)](step, *steps)

    def _setup(self):
        super()._setup()
        self._loop = True

    def _serve(self):
        while self._loop:
            step, appt = next(self._steps)
            if appt.is_ready():
                step()  # step(appt)
            else:
                self._l(LOG).debug("Next run delay: %s", appt.delay)
                tick = min(appt.delay, self._max_sleep)
                self._l(LOG).debug("Sleeping tick: %s", tick)
                time.sleep(tick)

    def _stop(self):
        self._loop = False

    def _check_alive(self) -> None:
        return
