import abc
import os
import pathlib
import signal
import sys
import typing as t

from daemon import daemon  # type: ignore

from garson._lib import constants as c
from garson.rcs import base


class AbstractSignalHook(abc.ABC):

    def __init__(self, signals: t.Iterable[int]):
        self._signals = tuple(signals)

    @property
    def signals(self):
        return self._signals

    @abc.abstractmethod
    def _call(self, sig, frame):
        raise NotImplementedError()

    def __call__(self, sig, frame):
        sig = signal.Signals(sig)
        print(f"Process signal received: {sig!r}")
        print(f"Calling handler: {self!r}")
        self._call(sig, frame)


class StopSignalHook(AbstractSignalHook):

    def __init__(self, svc, signals=(signal.SIGTERM, signal.SIGINT)):
        super().__init__(signals)
        self._svc = svc

    # TODO(d.burmistrov): pass signal/frame to `stop()`?
    def _call(self, sig, frame):
        self._svc.stop()


class TouchSignalHook(AbstractSignalHook):

    def __init__(self, path: str, signals=(signal.SIGUSR1,)):
        super().__init__(signals)
        self.path = pathlib.Path(path)

    def _call(self, sig, frame):
        self.path.touch()


# TODO(d.burmistrov): debug messages about signal hook invocations
class DaemonizeRc(base.AbstractServiceRunControl):

    def __init__(self, service, hooks=None):
        self._svc = service
        # TODO(d.burmistrov): defaultdict(list) - mulitiple hooks for 1 signal
        self._hooks = {sig: hook
                       for hook in hooks or {}
                       for sig in hook.signals}
        stop = StopSignalHook(self._svc)
        self._hooks.setdefault(signal.SIGTERM, stop)
        self._hooks.setdefault(signal.SIGINT, stop)

        signal_map = daemon.make_default_signal_map() | self._hooks
        self._dtx = daemon.DaemonContext(stdin=sys.stdin,
                                         stdout=sys.stdout,
                                         stderr=sys.stderr,
                                         signal_map=signal_map,
                                         detach_process=False)

    def __enter__(self):
        self._dtx.open()
        self._svc.info.do_touch(c.INFO_PROCESS, pid=os.getpid())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._dtx.close()
