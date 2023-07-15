from __future__ import annotations

import contextlib
import signal

from garson.services import base
from garson.contexts import daemon as g_daemon


LOG = logging.getLogger(__name__)


class FakeService(abc.ABC):

    SERVICE_TYPE = "fake"

    def __init__(self, daemonize=True):
        if daemonize:
            self.context = g_daemon.DaemonContext(self)
        else:
            self.context = contextlib.nullcontext()

    def serve(self):
        self._l(LOG).info("Fakely serving...")
        with self.context:
            signal.pause()
        self._l(LOG).info("Fake serving finished.")

    def stop(self):
        self._l(LOG).info("Stopping...")
