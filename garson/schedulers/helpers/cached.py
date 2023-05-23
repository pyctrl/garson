from __future__ import annotations

import typing as t

from garson.schedulers import base


class cached(base.SchedulerInterface):

    def __init__(self, scheduler: base.SchedulerInterface):
        self._scheduler = scheduler
        self._cache: t.Optional[base.Appointment] = None

    def now(self) -> float:
        return self._scheduler.now()

    def schedule(self) -> base.Appointment:
        if self._cache is None or self._cache.is_ready():
            self._cache = self._scheduler.schedule()
            return self._cache

        return self._cache
