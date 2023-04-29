from __future__ import annotations

import abc
import dataclasses
import datetime
import typing as t

_F_DELAY = "delay"


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class Schedule:
    timestamp: float
    scheduled: float
    target: t.Callable
    scheduler: AbstractScheduler
    delay: float = dataclasses.field(init=False)

    def __post_init__(self):
        object.__setattr__(self, _F_DELAY, self.scheduled - self.timestamp)


class AbstractScheduler(abc.ABC):

    def __init__(self, name: str, target: t.Callable):
        if not name.isidentifier():
            raise ValueError("name must be identifier")
        self._name = name
        self._target = target

    @abc.abstractmethod
    def schedule(self) -> Schedule:
        raise NotImplementedError

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

    def run_forced(self, *args: t.Any, **kwargs: t.Any) -> t.Any:
        return self._target(*args, **kwargs)

    def run_if_scheduled(self, *args: t.Any, **kwargs: t.Any) -> t.Any:
        if self.schedule().delay <= 0:
            return self._target(*args, **kwargs)
