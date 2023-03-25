import abc
import logging
import signal

from garson.contexts import base as g_ctxs


logging.basicConfig(level=logging.DEBUG)  # TODO(d.burmistrov): dev only
LOG = logging.getLogger(__name__)


class AbstractService(abc.ABC):

    def __init__(self, operate=True, contexts=None):
        self._operate = operate
        self._ctxs = g_ctxs.Contexts(contexts)

    def _setup(self):
        self._ctxs.open()

    def _teardown(self):
        self._ctxs.close()

    def serve(self):
        try:
            LOG.info("Preparing to serve...")
            self._setup()
            LOG.info(("Fakely serving...", "Serving...")[self._operate])
            (signal.pause, self._serve)[self._operate]()
            LOG.info("Finished serving normally.")
        except Exception as e:
            LOG.info("Serving has failed: {exc}", {"exc": e})
            raise
        finally:
            LOG.info("Tearing down...")
            self._teardown()

    @abc.abstractmethod
    def _serve(self):
        raise NotImplementedError()

    def stop(self):
        LOG.info("Stopping...")


class S(AbstractService):

    def _serve(self):
        LOG.info("My service >> serving <<")
        LOG.info("My service >> sleeping <<")
        signal.pause()
        LOG.info("My service >> finished <<")


if __name__ == "__main__":
    s = S()
    s.serve()
