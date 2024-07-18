import contextlib
import logging

from garson._lib import utils

LOG = logging.getLogger(__name__)


class AbstractServiceRunControl(
    contextlib.AbstractContextManager,
    utils.PackableMixin,
):
    pass


# TODO(d.burmistrov): make it a context manager?
class ServiceRunControls:

    def __init__(self, rcs=None):
        self._rcs = rcs or []
        self._stack = None

    def register_rc(self, packed_rc):
        self._rcs.append(packed_rc)

    def open(self):
        self._stack = contextlib.ExitStack()
        LOG.info("Entering run controls...")
        ctx_count = len(self._rcs)
        for i, ctx in enumerate(self._rcs, start=1):
            LOG.info("Entering run control %s/%s...", i, ctx_count)
            self._stack.enter_context(ctx())
        LOG.debug("Entered all run controls.")

    def close(self):
        LOG.info("Leaving run run controls...")
        self._stack.close()
        self._stack = None
        LOG.debug("Left all run controls.")
