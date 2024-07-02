from __future__ import annotations

import abc
import dataclasses


_F_TIMESTAMP = "timestamp"


@dataclasses.dataclass(order=True)
# @dataclasses.dataclass(order=True, frozen=True, kw_only=True, slots=True)
class Appointment:
    timestamp: float
    planned: float
    scheduler: SchedulerInterface

    @property
    def delay(self) -> float:
        return self.planned - self.timestamp

    # # TODO(d.burmistrov): think...
    # def __bool__(self):
    #     return self.is_ready()

    def is_ready(self) -> bool:
        self.refresh()
        return self.timestamp >= self.planned

    def refresh(self) -> None:
        object.__setattr__(self, _F_TIMESTAMP, self.scheduler.now())


class SchedulerInterface(abc.ABC):

    def __init__(self, *, name: str | None = None):
        name = name or type(self).__name__
        if not name.isidentifier():
            raise ValueError("name must be identifier")
        self.name = name

    @abc.abstractmethod
    def now(self) -> float:
        raise NotImplementedError

    @abc.abstractmethod
    def schedule(self) -> Appointment:
        raise NotImplementedError


class BaseProxyScheduler(SchedulerInterface, abc.ABC):

    def __init__(self, *, scheduler: SchedulerInterface, **kwargs):
        scheduler.now()  # sanity check
        self._sched = scheduler
        super().__init__(**kwargs)

    def _pre_proxy_hook(self, item):
        pass

    def _post_proxy_hook(self, item, attr):
        pass

    def __getattr__(self, item):
        self._pre_proxy_hook(item)
        attr = getattr(self._sched, item)
        self._post_proxy_hook(item, attr)
        return attr


class BaseScheduler(SchedulerInterface):

    @abc.abstractmethod
    def _schedule(self, now: float) -> float:
        raise NotImplementedError

    def schedule(self) -> Appointment:
        now = self.now()
        return Appointment(timestamp=now,
                           planned=self._schedule(now=now),
                           scheduler=self)
