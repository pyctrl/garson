from __future__ import annotations

import datetime
import time
import typing as t

from garson._lib import constants as c
from garson.schedulers import base


# TODO(d.burmistrov): , shift: int | float = 0
class IntervalScheduler(base.AbstractScheduler):

    def __init__(self, step_period: int | float = 1):
        super().__init__()
        self._step_interval = step_period
        self._next_launch = -c.INF
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
