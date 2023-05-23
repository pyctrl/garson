import os
import signal
import sys

import daemon  # type: ignore

from garson._lib import constants as c


class DaemonContext:

    def __init__(self, svc):
        self._svc = svc
        signal_map = daemon.daemon.make_default_signal_map()
        # TODO(d.burmistrov): pass signal/frame to `stop()`?
        signal_map[signal.SIGTERM] = lambda sig, frame: self._svc.stop()
        signal_map[signal.SIGINT] = signal_map[signal.SIGTERM]
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
