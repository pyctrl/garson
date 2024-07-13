import contextlib
import logging

from garson._lib import utils

LOG = logging.getLogger(__name__)


class AbstractBaseMiddleware(
    contextlib.AbstractContextManager,
    utils.PackableMixin,
):
    pass


# TODO(d.burmistrov): make it a context manager?
class Contexts:

    def __init__(self, contexts=None):
        self._contexts = contexts or []
        self._stack = None

    def register_context(self, packed_context):
        self._contexts.append(packed_context)

    def open(self):
        self._stack = contextlib.ExitStack()
        LOG.info("Entering contexts...")
        ctx_count = len(self._contexts)
        for i, ctx in enumerate(self._contexts, start=1):
            LOG.info("Entering context %s/%s...", i, ctx_count)
            self._stack.enter_context(ctx())
        LOG.debug("Entered all contexts.")

    def close(self):
        LOG.info("Leaving contexts...")
        self._stack.close()
        self._stack = None
        LOG.debug("Left all contexts.")
