from __future__ import annotations

import datetime
import time
import typing as t

from garson._lib import constants as c
from garson.schedulers import base


class IntervalScheduler(base.BaseScheduler):

    def __init__(self,
                 name: t.Optional[str] = None,
                 interval: int | float | datetime.timedelta = 1,
                 shift: int | float | datetime.timedelta = 0):
        if isinstance(shift, datetime.timedelta):
            shift = shift.total_seconds()

        if isinstance(interval, datetime.timedelta):
            self._interval = interval.total_seconds()
        else:
            self._interval = interval

        self._next_launch = (time.monotonic() + shift) if shift else -c.INF

        super().__init__(name=name)

    def now(self):
        return time.monotonic()

    def _schedule(self, now: float) -> float:
        if now < self._next_launch:
            return self._next_launch

        self._next_launch = now + self._interval
        return now
