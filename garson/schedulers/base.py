import abc
import operator


class AbstractScheduler(abc.ABC):

    @abc.abstractmethod
    def schedule(self) -> tuple[float, float]:
        raise NotImplementedError

    @abc.abstractmethod
    def set_next_step_schedule(self, *, delta=None, timestamp=None
                               ) -> tuple[float, float]:
        raise NotImplementedError

    @abc.abstractmethod
    def unset_next_step_schedule(self) -> tuple[float, float]:
        raise NotImplementedError

    def run_if_scheduled(self, func, *args, **kwargs):
        if operator.ge(*self.schedule()):
            return func(*args, **kwargs)
