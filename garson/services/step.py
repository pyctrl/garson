from __future__ import annotations

import abc
import datetime
import logging
import time
import typing as t

from garson.services import base


logging.basicConfig(level=logging.DEBUG)  # TODO(d.burmistrov): dev only
LOG = logging.getLogger(__name__)


def calculate_poke_time(scheduler: Scheduler,
                        disabled=False, minimal=0.1, delimeter=10, value=None):
    if disabled:
        return float("inf")
    if value:
        return value
    return min(scheduler._step_interval / delimeter, minimal)


class Scheduler:

    def __init__(self, service, step_period: int | float = 1):
        self._service = service
        self._step_interval = step_period
        self._next_launch = -float("inf")
        self._scheduled: t.Optional[float] = None

    def schedule(self) -> tuple[float, float]:
        now = time.monotonic()

        if self._scheduled:
            if now < self._scheduled:
                return now, self._scheduled

            self._scheduled = None
            self._next_launch = now + self._step_interval
            return now, now

        if now < self._next_launch:
            return now, self._next_launch

        self._next_launch = now + self._step_interval
        return now, now

    # TODO(d.burmistrov): reset scheduling
    def _set_next_step_delay(self,
                             delay: int | float | datetime.timedelta,
                             ) -> tuple[float, float]:
        if isinstance(delay, datetime.timedelta):
            delay = delay.total_seconds()

        now = time.monotonic()
        self._scheduled = now + delay
        return now, self._scheduled

    def set_next_step(self, *, delta=None, timestamp=None,
                      ) -> tuple[float, float]:
        # TODO(d.burmistrov): match-case?
        if delta is timestamp is None:
            raise TypeError("Missing argument")
        elif timestamp is None:
            return self._set_next_step_delay(delta)
        elif isinstance(timestamp, datetime.datetime):
            pass
        elif isinstance(timestamp, datetime.date):
            timestamp = datetime.datetime.fromordinal(timestamp.toordinal())

        delta = timestamp - datetime.datetime.utcnow()
        return self._set_next_step_delay(delta)


class StepService(base.AbstractService):

    def __init__(self, scheduler, poke_time=None,
                 operate=True, contexts=None, daemonize=True):
        super().__init__(operate=operate,
                         contexts=contexts,
                         daemonize=daemonize)
        self._sched: Scheduler = scheduler(self)
        self._poke_time = poke_time or calculate_poke_time(self._sched)
        self._loop = False

    def _setup(self):
        super()._setup()
        self._loop = True

    def _serve(self):
        while self._loop:
            now, next_launch = self._sched.schedule()
            if now >= next_launch:
                self._step(scheduler=self._sched)
                now = time.monotonic()

            if (delay := next_launch - now) > 0:
                time.sleep(min(delay, self._poke_time))

    def _stop(self):
        self._loop = False

    @abc.abstractmethod
    def _step(self, scheduler):
        raise NotImplementedError()


class S(StepService):

    def _step(self, scheduler):
        LOG.info("My service >> step <<")
        delta = datetime.timedelta(seconds=3)
        dt = datetime.datetime.utcnow()
        scheduler.set_next_step(timestamp=(dt + delta))
        scheduler.set_next_step(delta=0.5)


if __name__ == "__main__":
    S(Scheduler, 1).serve()
