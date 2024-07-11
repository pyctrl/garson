import os
import signal
import sys

import daemon  # type: ignore

from garson._lib import constants as c
from garson._lib import utils
from garson.middlewares.daemon import sig_hooks


# TODO(d.burmistrov): debug messages about signal hook invocations
class DaemonizeMiddleware(utils.PackableMixin):

    def __init__(self, service, hooks=None):
        self._svc = service
        self._hooks = {sig: hook
                       for hook in hooks or {}
                       for sig in hook.signals}
        stop = sig_hooks.StopSignalHook(self._svc)
        self._hooks.setdefault(signal.SIGTERM, stop)
        self._hooks.setdefault(signal.SIGINT, stop)

        signal_map = daemon.daemon.make_default_signal_map() | self._hooks
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
