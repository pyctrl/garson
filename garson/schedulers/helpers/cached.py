from __future__ import annotations

import typing as t

from garson.schedulers import base


class cached(base.SchedulerInterface):

    def __init__(self, scheduler: base.SchedulerInterface):
        self._scheduler = scheduler
        self._cache: t.Optional[base.Appointment] = None

    # iface

    def now(self) -> float:
        return self._scheduler.now()

    def schedule(self) -> base.Appointment:
        if self._cache is None or self._cache.is_ready():
            self._cache = self._scheduler.schedule()
            return self._cache

        return self._cache

    def run(self,
            args: t.Optional[list[t.Any] | tuple[t.Any]] = None,
            kwargs: t.Optional[dict[str, t.Any]] = None,
            force: bool = False,
            ) -> t.Union[tuple[t.Literal[True], t.Any],
                         tuple[t.Literal[False], base.Appointment]]:
        if force:
            self._cache = None

        if self._cache is None or self._cache.is_ready():
            res = self._scheduler.run(args=args, kwargs=kwargs, force=force)
            self._cache = self._scheduler.schedule() if res[0] else res[1]
            return res

        return False, self._cache
