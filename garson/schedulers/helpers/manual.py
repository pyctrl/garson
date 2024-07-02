from __future__ import annotations

import datetime
import typing as t

from garson.schedulers import base


class manual(base.SchedulerInterface):

    def __init__(self, *, scheduler: base.SchedulerInterface, **kwargs):
        super().__init__(**kwargs)
        self._sched = scheduler
        self._appointed: t.Optional[base.Appointment] = None

    def __repr__(self):
        return self.__class__.__qualname__

    # iface

    def now(self) -> float:
        return self._sched.now()

    def schedule(self) -> base.Appointment:
        if self._appointed is None:
            return self._sched.schedule()
        self._appointed.refresh()
        return self._appointed

    # manual scheduled

    def __set_delay(self, delay: int | float | datetime.timedelta,
                    ) -> base.Appointment:
        if isinstance(delay, datetime.timedelta):
            delay = delay.total_seconds()

        s = self._sched.schedule()
        self._appointed = base.Appointment(timestamp=s.timestamp,
                                           planned=s.timestamp + delay,
                                           scheduler=self)
        return self._appointed

    def __set_ts(self, ts: int | float | datetime.date) -> base.Appointment:
        if isinstance(ts, (int, float)):
            return self.__set_delay(ts - self._sched.now())

        if isinstance(ts, datetime.datetime):
            pass
        elif isinstance(ts, datetime.date):
            ts = datetime.datetime.fromordinal(ts.toordinal())

        delay = ts - datetime.datetime.utcnow()
        return self.__set_delay(delay)

    def appoint_next(  # manual
            self,
            *,
            delay: t.Optional[int | float | datetime.timedelta] = None,
            timestamp: t.Optional[int | float | datetime.date] = None,
    ) -> base.Appointment:
        if delay is timestamp is None:
            raise TypeError("Missing argument")
        elif (delay is not None) and (timestamp is not None):
            raise TypeError("Bad arguments")
        elif delay is not None:
            return self.__set_delay(delay)
        else:
            return self.__set_ts(timestamp)  # type: ignore[arg-type] # noqa: E501

    def reset_next(self) -> base.Appointment:
        # TODO(d.burmistrov): check if no manual schedule? raise if not?
        self._appointed = None
        return self._sched.schedule()
