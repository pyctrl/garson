from __future__ import annotations

import abc
import datetime
import logging
import time
import typing as t

from garson.services import base


logging.basicConfig(level=logging.DEBUG)  # TODO(d.burmistrov): dev only
LOG = logging.getLogger(__name__)


class Scheduler(abc.ABC):

    @abc.abstractmethod
    def schedule(self) -> tuple[float, float]:
        raise NotImplementedError

    @abc.abstractmethod
    def set_next_step_schedule(self, *, delta=None, timestamp=None
                               ) -> tuple[float, float]:
        raise NotImplementedError

    @abc.abstractmethod
    def unset_next_step_schedule(self) -> tuple[float, float]:
        raise NotImplementedError


class IntervalScheduler(Scheduler):

    def __init__(self, step_period: int | float = 1):
        super().__init__()
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

    def _set_next_step_delay(self,
                             delay: int | float | datetime.timedelta,
                             ) -> tuple[float, float]:
        if isinstance(delay, datetime.timedelta):
            delay = delay.total_seconds()

        now = time.monotonic()
        self._scheduled = now + delay
        return now, self._scheduled

    def set_next_step_schedule(self, *, delta=None, timestamp=None,
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

    def unset_next_step_schedule(self) -> tuple[float, float]:
        self._scheduled = None
        return time.monotonic(), self._next_launch


class StepService(base.AbstractService):

    def __init__(self,
                 scheduler: Scheduler,
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
            else:
                self._step(scheduler=self._sched)

    def _stop(self):
        self._loop = False

    @abc.abstractmethod
    def _step(self, scheduler):
        raise NotImplementedError()


class S(StepService):

    def _step(self, scheduler):
        dt = datetime.datetime.utcnow()
        LOG.info("My service >> step << %s", dt)
        delta = datetime.timedelta(seconds=3)
        scheduler.set_next_step_schedule(timestamp=(dt + delta))
        scheduler.set_next_step_schedule(delta=10.5)


def main():
    S(IntervalScheduler(3)).serve()


if __name__ == "__main__":
    main()
