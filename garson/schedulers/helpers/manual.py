from __future__ import annotations

import datetime
import typing as t

from garson.schedulers import base


class manual(base.SchedulerInterface):

    def __init__(self, scheduler: base.SchedulerInterface):
        self._scheduler = scheduler
        self._manual_scheduled: t.Optional[base.Schedule] = None

    # iface

    def now(self) -> float:
        return self._scheduler.now()

    def schedule(self) -> base.Schedule:
        if self._manual_scheduled is None:
            return self._scheduler.schedule()
        self._manual_scheduled.refresh()
        return self._manual_scheduled

    def run(self,
            args: t.Optional[list[t.Any] | tuple[t.Any]] = None,
            kwargs: t.Optional[dict[str, t.Any]] = None,
            force: bool = False,
            ) -> t.Union[tuple[t.Literal[True], t.Any],
                         tuple[t.Literal[False], base.Schedule]]:
        if force:
            self._manual_scheduled = None

        if self._manual_scheduled is None:
            return self._scheduler.run(args=args, kwargs=kwargs, force=force)
        elif self._manual_scheduled.is_ready():
            self._manual_scheduled = None
            return self._scheduler.run(args=args, kwargs=kwargs, force=True)
        else:
            return False, self._manual_scheduled

    # manual scheduled

    def _set_next_run_delay(self, delay: int | float | datetime.timedelta,
                            ) -> base.Schedule:
        if isinstance(delay, datetime.timedelta):
            delay = delay.total_seconds()

        s = self._scheduler.schedule()
        self._manual_scheduled = base.Schedule(timestamp=s.timestamp,
                                               appointed=s.timestamp + delay,
                                               scheduler=self,
                                               iteration=s.iteration)
        return self._manual_scheduled

    def _set_next_run_timestamp(self, timestamp: int | float | datetime.date,
                                ) -> base.Schedule:
        if isinstance(timestamp, (int, float)):
            return self._set_next_run_delay(timestamp - self._scheduler.now())

        if isinstance(timestamp, datetime.datetime):
            pass
        elif isinstance(timestamp, datetime.date):
            timestamp = datetime.datetime.fromordinal(timestamp.toordinal())

        delay = timestamp - datetime.datetime.utcnow()
        return self._set_next_run_delay(delay)

    def set_next_run_schedule(  # manual
            self,
            *,
            delay: t.Optional[int | float | datetime.timedelta] = None,
            timestamp: t.Optional[int | float | datetime.date] = None,
    ) -> base.Schedule:
        if delay is timestamp is None:
            raise TypeError("Missing argument")
        elif (delay is not None) and (timestamp is not None):
            raise TypeError("Bad arguments")
        elif delay is not None:
            return self._set_next_run_delay(delay)
        else:
            return self._set_next_run_timestamp(timestamp)  # type: ignore[arg-type] # noqa: E501

    def unset_next_run_schedule(self) -> base.Schedule:
        # TODO(d.burmistrov): check if no manual schedule? raise if not?
        self._manual_scheduled = None
        return self._scheduler.schedule()
