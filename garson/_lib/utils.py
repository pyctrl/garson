import contextlib
import datetime
import sys
import typing as t

T = t.TypeVar("T")


def make_qualname(obj: object):
    type_ = type(obj)
    return f"{type_.__module__}.{type_.__qualname__}"


@contextlib.contextmanager
def measure(info):
    start = info.start = datetime.datetime.utcnow()
    tb = True
    try:
        yield
        tb = False
    finally:
        end = info.end = datetime.datetime.utcnow()
        info.duration = end - start
        info.tb = tb
        if tb:
            info.exc_type, info.exc_value, _ = sys.exc_info()
        else:
            info.exc_type = info.exc_value = None


class Packed(t.Generic[T]):
    def __init__(self, func: t.Type[T], *args, **kwargs):
        self.func = func
        self.args = list(args)
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs) -> T:
        return self.func(*self.args, *args, **self.kwargs, **kwargs)

    def pack(self, *args, **kwargs):
        self.args.extend(args)
        self.kwargs.update(kwargs)
        return self


class PackableMixin:

    @classmethod
    def pack(cls, *args, **kwargs):
        return Packed(cls, *args, **kwargs)
