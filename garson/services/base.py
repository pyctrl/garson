from __future__ import annotations

import abc
import contextlib
import datetime
import functools
import logging
import sys
import uuid
import weakref

from garson._lib import constants as c
from garson._lib import info as i
from garson._lib import log
from garson._lib import utils
from garson.rcs import base as rcs


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

    @abc.abstractmethod
    def stop(self) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def serve(self):
        raise NotImplementedError()


class BaseService(AbstractService, abc.ABC):

    SERVICE_TYPE = "untyped"

    def __init__(self, log_adapter=log.LogAdapter):
        self._rcs = rcs.ServiceRunControls()
        self._failed = False
        self._serving = False
        self.info = i.Info()
        self._reset_info()
        self._log_adapter = log_adapter
        self._loggers = weakref.WeakKeyDictionary()

    def register_rc(self, packed_rc: utils.Packed):
        self._rcs.register_rc(packed_rc.pack(service=self))

    def _l(self, logger):
        if logger not in self._loggers:
            wrapped = self._log_adapter(logger=logger,
                                        extra=dict(info=self.info))
            self._loggers[logger] = wrapped
        return self._loggers[logger]

    def _reset_info(self):
        self.info.do_clear()
        self.info.do_touch(c.INFO_SERVICE,
                           name=type(self).__name__,
                           qual_name=utils.make_qualname(self),
                           type=self.SERVICE_TYPE,
                           instance_id=uuid.uuid4().hex)

    def _setup(self):
        self._rcs.open()

    def _teardown(self):
        self._rcs.close()

    def __enter__(self):
        self._l(LOG).info("Preparing to serve...")
        self._reset_info()
        info = self.info.do_touch(c.INFO_SERVE,
                                  launch_id=uuid.uuid4().hex)
        self._setup()
        info.start = datetime.datetime.utcnow()
        return self

    def __exit__(self, t, v, tb):
        info = self.info.serve
        info.end = datetime.datetime.utcnow()
        info.duration = info.end - info.start
        info.do_update(tb=bool(t), exc_type=t, exc_value=v)
        self._l(LOG).info("Tearing down...")
        self._teardown()

    def serve(self):
        with self:
            self._l(LOG).info("Serving...")
            self._serving = True
            try:
                self._serve()
            except Exception as e:
                self._l(LOG).info("Serving has failed: %s", e)
                raise
            else:
                self._l(LOG).info("Finished serving normally.")

    @abc.abstractmethod
    def _serve(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def _stop(self):
        raise NotImplementedError()

    def stop(self) -> None:
        self._l(LOG).info("Stopping...")
        self._stop()

    def die(self, code: int = 1, msg: str | None = None) -> None:
        reason = "Emergency exit!"
        if msg:
            reason = f"{reason} Message: {msg}"
        self._l(LOG).warning(reason)
        sys.exit(code)

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
