from __future__ import annotations

from garson.schedulers import base


class cached(base.BaseProxyScheduler):

    def __init__(self, *, scheduler: base.SchedulerInterface, **kwargs):
        super().__init__(scheduler=scheduler, **kwargs)
        self._stub = base.Appointment(timestamp=0, planned=0, scheduler=self)
        self._cache: base.Appointment = self._stub

    def __repr__(self):
        return self.__class__.__qualname__

    def now(self) -> float:
        return self._sched.now()

    def schedule(self) -> base.Appointment:
        if self._cache.is_ready():
            self._cache = self._sched.schedule()

        return self._cache

    def _post_proxy_hook(self, item, attr):
        self._cache = self._stub
        super()._post_proxy_hook(item, attr)
