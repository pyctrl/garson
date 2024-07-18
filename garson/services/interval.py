from __future__ import annotations

import abc
import datetime
import logging
import time
import typing as t

from garson._lib import constants as c
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
            appointment = candidate.schedule()
            delay = appointment.delay
            if delay <= 0:
                base_index = (index + 1) % iterations_count
                result = appointment
                iteration = candidate
                break
            if delay < result.delay:
                base_index = (index + 1) % iterations_count
                result = appointment
        yield iteration, result


class AbstractIteration(abc.ABC, utils.PackableMixin):

    def __init__(self,
                 service: IterationService,
                 scheduler: sched.SchedulerInterface,
                 info: i.Info,
                 name: t.Optional[str] = None):
        self.name = name or self.__class__.__name__
        self.service = service
        self._scheduler = scheduler
        self._iteration = 1
        self.info = info.do_touch(c.INFO_ITERATION)

        self._reset_info()

    def _l(self, logger):
        return self.service._l(logger)

    def _reset_info(self):
        self.info.do_clear()
        self.info.do_update(name=self.name,
                            qual_name=utils.make_qualname(self),
                            iteration=self._iteration)

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

    @abc.abstractmethod
    def _iterate(self):
        raise NotImplementedError


class IterationService(base.BaseService):

    SERVICE_TYPE = "iteration"

    _STRATEGIES = (_strategy_single, _strategy_multi_1)

    def __init__(self, tick: int | float | datetime.timedelta = 1):
        # TODO(d.burmistrov): allow strategy as parameter
        super().__init__()
        self._should_run = False

        if isinstance(tick, datetime.timedelta):
            tick = tick.total_seconds()
        self._tick = tick

        self._iterations: list = []
        self._iqueue = None

    def register_iteration(
            self,
            scheduler_pack: utils.Packed[sched.SchedulerInterface],
            iteration_pack: utils.Packed[AbstractIteration],
    ):
        packed = iteration_pack.pack(scheduler=scheduler_pack())
        self._iterations.append(packed)

    def _setup(self):
        super()._setup()

        strategy = self._STRATEGIES[bool(len(self._iterations) > 1)]
        self._iqueue = strategy(*(it(service=self, info=self.info)
                                  for it in self._iterations))

        self._should_run = True

    def _serve(self):
        while self._should_run:
            iteration, appointment = next(self._iqueue)
            if appointment.is_ready():
                iteration()  # iteration(appointment)
            else:
                self._l(LOG).debug("Next run delay: %s", appointment.delay)
                tick = min(appointment.delay, self._tick)
                self._l(LOG).debug("Sleeping tick: %s", tick)
                time.sleep(tick)

    def _stop(self):
        self._should_run = False

    def _check_alive(self) -> None:
        return
