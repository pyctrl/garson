from __future__ import annotations

import abc
import datetime
import logging
import time
import typing as t

from garson._lib import info as i
from garson._lib import utils
from garson.schedulers import base as sched
from garson.services import base


LOG = logging.getLogger(__name__)


def _strategy_single(iteration):
    while True:
        yield iteration, iteration.schedule()


def _strategy_multi_1(*iterations):
    base_index = 0
    iterations_count = len(iterations)
    while True:
        iteration = iterations[base_index]
        result = iteration.schedule()
        for j in range(1, iterations_count):
            index = (base_index + j) % iterations_count
            candidate = iterations[index]
            appt = candidate.schedule()
            delay = appt.delay
            if delay <= 0:
                base_index = (index + 1) % iterations_count
                result = appt
                iteration = candidate
                break
            if delay < result.delay:
                base_index = (index + 1) % iterations_count
                result = appt
        yield iteration, result


class AbstractIteration(abc.ABC):

    def __init__(self,
                 scheduler: sched.SchedulerInterface,
                 name: t.Optional[str] = None):
        self.name = name or type(self).__name__
        self._scheduler = scheduler
        self.service: t.Optional[IterationService] = None
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
            ">> Starting '%s' iteration=%d",
            self.name, self._iteration,
        )
        try:
            with utils.measure(self.info):
                self._iterate()
            self._l(LOG).debug(
                "<< '%s' iteration=%d successfully finished",
                self.name, self._iteration,
            )
        except Exception as e:
            self._l(LOG).exception(
                "<< [!!] '%s' iteration=%d has failed: %s",
                self.name, self._iteration, e,
            )
        finally:
            self._iteration += 1

    def schedule(self) -> sched.Appointment:
        return self._scheduler.schedule()

    def attach_service(self, service: IterationService) -> None:
        self.service = service

    @abc.abstractmethod
    def _iterate(self):
        raise NotImplementedError


class IterationService(base.AbstractService):

    SERVICE_TYPE = "iteration"

    _STRATEGIES = (_strategy_single, _strategy_multi_1)

    def __init__(self,
                 iteration: AbstractIteration,
                 *iterations: AbstractIteration,
                 gap: int | float | datetime.timedelta = 1,
                 contexts=None):
        # TODO(d.burmistrov): allow strategy as parameter
        super().__init__(contexts=contexts)
        self._loop = False

        if isinstance(gap, datetime.timedelta):
            gap = gap.total_seconds()
        self._max_sleep = gap

        iteration.attach_service(self)
        for itn in iterations:
            itn.attach_service(self)

        self._iterations = (
            self._STRATEGIES[bool(iterations)](iteration, *iterations)
        )

    def _setup(self):
        super()._setup()
        self._loop = True

    def _serve(self):
        while self._loop:
            iteration, appt = next(self._iterations)
            if appt.is_ready():
                iteration()  # iteration(appt)
            else:
                self._l(LOG).debug("Next run delay: %s", appt.delay)
                tick = min(appt.delay, self._max_sleep)
                self._l(LOG).debug("Sleeping tick: %s", tick)
                time.sleep(tick)

    def _stop(self):
        self._loop = False

    def _check_alive(self) -> None:
        return
