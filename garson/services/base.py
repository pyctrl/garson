import abc
import contextlib
import functools
import logging
import signal

from garson.contexts import base as g_ctxs
from garson.contexts import daemon as g_daemon


LOG = logging.getLogger(__name__)


class MarkedFailedError(Exception):
    pass


def _mark_failed(method):
    @functools.wraps(method)
    def decorated(self, *args, **kwargs):
        if self._failed:
            raise MarkedFailedError()

        return method(self, *args, **kwargs)

    return decorated


class AbstractService(abc.ABC):

    def __init__(self, operate=True, contexts=None, daemonize=True):
        self._operate = operate
        contexts = contexts or []
        if daemonize:
            contexts.append(g_daemon.DaemonContext(self))
        self._ctxs = g_ctxs.Contexts(contexts)
        self._failed = False
        self._serving = False

    def _setup(self):
        self._ctxs.open()

    def _teardown(self):
        self._ctxs.close()

    def serve(self):
        try:
            LOG.info("Preparing to serve...")
            self._setup()
            LOG.info(("Fakely serving...", "Serving...")[self._operate])
            self._serving = True
            (signal.pause, self._serve)[self._operate]()
            LOG.info("Finished serving normally.")
        except Exception as e:
            LOG.info("Serving has failed: %s", e)
            raise
        finally:
            LOG.info("Tearing down...")
            self._teardown()

    @abc.abstractmethod
    def _serve(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def _stop(self):
        raise NotImplementedError()

    def stop(self):
        LOG.info("Stopping...")
        if self._operate:
            self._stop()

    # new - thinking
    def mark_failed(self) -> None:
        self._failed = False
        raise MarkedFailedError()

    def is_alive(self) -> bool:
        with contextlib.suppress(Exception):
            self.check_alive()
            return True
        return False

    @_mark_failed
    def check_alive(self) -> None:  # liveness probe
        return self._check_alive()

    @abc.abstractmethod
    def _check_alive(self) -> None:
        raise NotImplementedError

    # guards
    #
    # @abc.abstractmethod
    # def _refresh(self) -> None:
    #     raise NotImplementedError
    #
    # @_mark_failed
    # def refresh(self, force: bool = False) -> None:
    #     if force:
    #         return self._refresh()
    #
    #     return self._sched.run_if_scheduled(self._refresh)
