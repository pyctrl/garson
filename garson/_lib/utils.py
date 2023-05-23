import contextlib
import datetime
import sys


def make_qualname(obj: object):
    t = type(obj)
    return f"{t.__module__}.{t.__qualname__}"


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
