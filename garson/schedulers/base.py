from __future__ import annotations

import abc
import dataclasses
import typing as t


_F_TIMESTAMP = "timestamp"


# @dataclasses.dataclass(order=True)
@dataclasses.dataclass(order=True, frozen=True, kw_only=True, slots=True)
class Appointment:
    timestamp: float
    planned: float
    scheduler: SchedulerInterface
    iteration: int

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

    def __init__(self, name: str, target: t.Callable):
        self.name = name
        self._target = target

    @abc.abstractmethod
    def now(self) -> float:
        raise NotImplementedError

    @abc.abstractmethod
    def schedule(self) -> Appointment:
        raise NotImplementedError

    # TODO(d.burmistrov): schedule argument optional? and rename?
    def run(self,
            args: t.Optional[list[t.Any] | tuple[t.Any]] = None,
            kwargs: t.Optional[dict[str, t.Any]] = None,
            force: bool = False,
            ) -> t.Union[tuple[t.Literal[True], t.Any],
                         tuple[t.Literal[False], Appointment]]:
        raise NotImplementedError


class BaseScheduler(SchedulerInterface):

    def __init__(self, name: str, target: t.Callable):
        super().__init__(name=name, target=target)
        if not name.isidentifier():
            raise ValueError("name must be identifier")
        self._running = False
        self._iterations = 0

    @property
    def _next_iteration(self) -> int:
        return self._iterations + 1

    @abc.abstractmethod
    def _schedule(self, now: float) -> float:
        raise NotImplementedError

    def schedule(self) -> Appointment:
        now = self.now()
        return Appointment(timestamp=now,
                           planned=self._schedule(now=now),
                           scheduler=self,
                           iteration=self._next_iteration)

    def run(self,
            args: t.Optional[list[t.Any] | tuple[t.Any]] = None,
            kwargs: t.Optional[dict[str, t.Any]] = None,
            force: bool = False,
            ) -> t.Union[tuple[t.Literal[True], t.Any],
                         tuple[t.Literal[False], Appointment]]:
        self._iterations = self._next_iteration
        self._running = True
        try:
            return True, self._target(*(args or tuple()), **(kwargs or {}))
        finally:
            self._running = False
