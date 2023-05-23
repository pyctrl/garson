from __future__ import annotations

import abc
import dataclasses
import typing as t


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

    def __init__(self, name: str):
        self.name = name

    @abc.abstractmethod
    def now(self) -> float:
        raise NotImplementedError

    @abc.abstractmethod
    def schedule(self) -> Appointment:
        raise NotImplementedError


class BaseScheduler(SchedulerInterface):

    def __init__(self, name: t.Optional[str] = None):
        name = name or type(self).__name__
        super().__init__(name=name)
        if not name.isidentifier():
            raise ValueError("name must be identifier")

    @abc.abstractmethod
    def _schedule(self, now: float) -> float:
        raise NotImplementedError

    def schedule(self) -> Appointment:
        now = self.now()
        return Appointment(timestamp=now,
                           planned=self._schedule(now=now),
                           scheduler=self)
