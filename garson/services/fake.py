from __future__ import annotations

import contextlib
import logging
import signal

from garson.contexts import daemon as g_daemon
from garson.services import base


LOG = logging.getLogger(__name__)


class FakeService(base.AbstractService):

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
