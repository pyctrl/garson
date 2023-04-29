from __future__ import annotations

import datetime
import time
import typing as t

from garson._lib import constants as c
from garson.schedulers import base


class IntervalScheduler(base.AbstractScheduler):

    def __init__(self,
                 name: str,
                 target: t.Callable,
                 interval: int | float = 1,
                 shift: int | float | datetime.timedelta = 0):
        super().__init__(name, target)
        self._interval = interval
        if isinstance(shift, datetime.timedelta):
            shift = shift.total_seconds()
        self._next_launch = (time.monotonic() + shift) if shift else -c.INF
        self._scheduled: t.Optional[float] = None

    def schedule(self) -> base.Schedule:
        now = time.monotonic()

        if self._scheduled:
            if now < self._scheduled:
                return base.Schedule(timestamp=now,
                                     scheduled=self._scheduled,
                                     scheduler=self,
                                     target=self._target)

            self._scheduled = None
            self._next_launch = now + self._interval
            return base.Schedule(timestamp=now,
                                 scheduled=now,
                                 scheduler=self,
                                 target=self._target)

        if now < self._next_launch:
            return base.Schedule(timestamp=now,
                                 scheduled=self._next_launch,
                                 scheduler=self,
                                 target=self._target)

        self._next_launch = now + self._interval
        return base.Schedule(timestamp=now,
                             scheduled=now,
                             scheduler=self,
                             target=self._target)

    def _set_next_run_delay(self, delay: int | float | datetime.timedelta,
                            ) -> base.Schedule:
        if isinstance(delay, datetime.timedelta):
            delay = delay.total_seconds()

        now = time.monotonic()
        self._scheduled = now + delay
        return base.Schedule(timestamp=now,
                             scheduled=self._scheduled,
                             scheduler=self,
                             target=self._target)

    def _set_next_run_timestamp(self, timestamp: int | float | datetime.date,
                                ) -> base.Schedule:
        if isinstance(timestamp, (int, float)):
            return self._set_next_run_delay(timestamp - time.monotonic())

        if isinstance(timestamp, datetime.datetime):
            pass
        elif isinstance(timestamp, datetime.date):
            timestamp = datetime.datetime.fromordinal(timestamp.toordinal())

        delay = timestamp - datetime.datetime.utcnow()
        return self._set_next_run_delay(delay)

    def unset_next_run_schedule(self) -> base.Schedule:
        self._scheduled = None
        return base.Schedule(timestamp=time.monotonic(),
                             scheduled=self._next_launch,
                             scheduler=self,
                             target=self._target)
