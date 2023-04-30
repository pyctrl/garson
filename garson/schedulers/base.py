from __future__ import annotations

import abc
import dataclasses
import datetime
import typing as t

from garson._lib import constants as c


_F_DELAY = "delay"


# @dataclasses.dataclass(order=True, frozen=True, kw_only=True, slots=True)
@dataclasses.dataclass(order=True)
class Schedule:
    timestamp: float
    scheduled: float
    scheduler: AbstractScheduler
    iteration: int
    delay: float = dataclasses.field(init=False)

    def __post_init__(self):
        object.__setattr__(self, _F_DELAY, self.scheduled - self.timestamp)

    def is_ready(self) -> bool:
        return self.delay <= 0

    def refresh(self, now: float) -> Schedule:
        return type(self)(timestamp=now,
                          scheduled=self.scheduled,
                          scheduler=self.scheduler,
                          iteration=self.iteration)


# TODO(d.burmistrov): split into abstract and base classes
# class BaseScheduler(abc.ABC):
class AbstractScheduler(abc.ABC):

    def __init__(self, name: str, target: t.Callable):
        if not name.isidentifier():
            raise ValueError("name must be identifier")
        self.name = name
        self._target = target
        self._running = False
        self._iterations = 0
        self._scheduled: Schedule = self._schedule()

    @property
    def scheduled(self) -> Schedule:
        return self._scheduled

    @property
    def _next_iteration(self) -> int:
        return self._iterations + 1

    @abc.abstractmethod
    def now(self) -> float:
        raise NotImplementedError

    @abc.abstractmethod
    def _schedule(self) -> Schedule:
        raise NotImplementedError

    def schedule(self) -> Schedule:
        if self._scheduled.iteration != self._next_iteration:
            self._scheduled = self._schedule()
        else:
            self._scheduled = self._scheduled.refresh(self.now())
        return self._scheduled

    @abc.abstractmethod
    def _set_next_run_delay(self, delay: int | float | datetime.timedelta,
                            ) -> Schedule:
        raise NotImplementedError

    @abc.abstractmethod
    def _set_next_run_timestamp(self, timestamp: int | float | datetime.date,
                                ) -> Schedule:
        raise NotImplementedError

    def set_next_run_schedule(  # manual
            self,
            *,
            delay: t.Optional[int | float | datetime.timedelta] = None,
            timestamp: t.Optional[int | float | datetime.date] = None,
    ) -> Schedule:
        if delay is timestamp is None:
            raise TypeError("Missing argument")
        elif (delay is not None) and (timestamp is not None):
            raise TypeError("Bad arguments")
        elif delay is not None:
            return self._set_next_run_delay(delay)
        else:
            return self._set_next_run_timestamp(timestamp)  # type: ignore[arg-type] # noqa: E501

    @abc.abstractmethod
    def unset_next_run_schedule(self) -> Schedule:
        raise NotImplementedError

    # TODO(d.burmistrov): schedule argument optional? and rename?
    def run(self,
            args: t.Optional[list[t.Any] | tuple[t.Any]] = None,
            kwargs: t.Optional[dict[str, t.Any]] = None,
            # force
            ) -> t.Union[tuple[t.Literal[True], t.Any],
                         tuple[t.Literal[False], Schedule]]:
        if self._scheduled.iteration != self._next_iteration:
            self._scheduled = self._schedule()

        if not self._scheduled.is_ready():
            return False, self._schedule()

        self._iterations = self._scheduled.iteration
        self._running = True
        try:
            return True, self._target(*(args or tuple()), **(kwargs or {}))
        finally:
            self._running = False


class FakeScheduler(AbstractScheduler):

    def __init__(self,
                 name: str = "fake_scheduler",
                 target: t.Callable = lambda *args, **kwargs: None):
        super().__init__(name=name, target=target)
        self._fake_schedule = Schedule(timestamp=c.INF,
                                       scheduled=c.INF,
                                       scheduler=self,
                                       iteration=0)

    def now(self) -> float:
        return c.INF

    def _schedule(self) -> Schedule:
        return self._fake_schedule

    def _set_next_run_delay(self, delay: int | float | datetime.timedelta,
                            ) -> Schedule:
        return self._fake_schedule

    def _set_next_run_timestamp(self, timestamp: int | float | datetime.date,
                                ) -> Schedule:
        return self._fake_schedule

    def unset_next_run_schedule(self) -> Schedule:
        return self._fake_schedule
