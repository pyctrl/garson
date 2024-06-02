import abc
import pathlib
import signal

import daemon  # type: ignore


class AbstractSignalHook(abc.ABC):

    def __init__(self, signals):
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

    def __init__(self, path: str, sig=signal.SIGHUP):
        super().__init__((sig,))
        self.path = pathlib.Path(path)

    def _call(self, sig, frame):
        self.path.touch()
