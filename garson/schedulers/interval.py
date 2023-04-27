from __future__ import annotations

import datetime
import time
import typing as t

from garson._lib import constants as c
from garson.schedulers import base


class IntervalScheduler(base.AbstractScheduler):

    def __init__(self, step_period: int | float = 1, shift: int | float = 0):
        super().__init__()
        self._step_interval = step_period
        self._next_launch = (time.monotonic() + shift) if shift else -c.INF
        self._scheduled: t.Optional[float] = None

    def schedule(self) -> tuple[float, float, float]:
        now = time.monotonic()

        if self._scheduled:
            if now < self._scheduled:
                return self._scheduled - now, now, self._scheduled

            self._scheduled = None
            self._next_launch = now + self._step_interval
            return 0, now, now

        if now < self._next_launch:
            return self._next_launch - now, now, self._next_launch

        self._next_launch = now + self._step_interval
        return 0, now, now

    def _set_next_step_delay(self,
                             delay: int | float | datetime.timedelta,
                             ) -> tuple[float, float, float]:
        if isinstance(delay, datetime.timedelta):
            delay = delay.total_seconds()

        now = time.monotonic()
        self._scheduled = now + delay
        return self._scheduled - now, now, self._scheduled

    def set_next_step_schedule(self, *, delta=None, timestamp=None,
                               ) -> tuple[float, float, float]:
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

    def unset_next_step_schedule(self) -> tuple[float, float, float]:
        self._scheduled = None
        now = time.monotonic()
        return self._next_launch - now, now, self._next_launch
