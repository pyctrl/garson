from __future__ import annotations

import abc
import dataclasses
import datetime
import typing as t

_F_DELAY = "delay"


@dataclasses.dataclass(order=True, frozen=True, kw_only=True, slots=True)
class Schedule:
    timestamp: float = dataclasses.field(compare=False)
    scheduled: float = dataclasses.field(compare=False)
    target: t.Callable = dataclasses.field(compare=False)
    scheduler: AbstractScheduler = dataclasses.field(compare=False)
    iteration: int = dataclasses.field(compare=False)
    delay: float = dataclasses.field(init=False, compare=True)

    def __post_init__(self):
        object.__setattr__(self, _F_DELAY, self.scheduled - self.timestamp)

    def is_ready(self) -> bool:
        return self.delay <= 0

    def refresh(self, now: float):
        # return Schedule(
        return self.__class__(
            timestamp=now,
            scheduled=self.scheduled,
            target=self.target,
            scheduler=self.scheduler,
            iteration=self.iteration,
        )

    def run(self, *args: t.Any, **kwargs: t.Any) -> tuple[bool, t.Any]:
        return self.scheduler.run(self, *args, **kwargs)


# TODO(d.burmistrov): split into abstract and base classes
# class BaseScheduler(abc.ABC):
class AbstractScheduler(abc.ABC):

    def __init__(self, name: str, target: t.Callable):
        if not name.isidentifier():
            raise ValueError("name must be identifier")
        self._name = name
        self._target = target
        self._iterations = 0
        self._scheduled: t.Optional[Schedule] = None

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
        if self._scheduled is None:
            self._scheduled = self._schedule()
            return self._scheduled
        return self._scheduled.refresh(self.now())

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
    def run(self, schedule: Schedule, *args: t.Any, **kwargs: t.Any,
            ) -> tuple[bool, t.Any]:
        if (
                (self is schedule.scheduler)
                and (self._iterations < schedule.iteration)
                and schedule.is_ready()
        ):
            self._iterations += 1
            self._scheduled = None
            return True, schedule.target(*args, **kwargs)

        return False, None
