import logging


class LogAdapter(logging.LoggerAdapter):

    def __init__(self, logger, info, extra=None):
        self.info = info
        super().__init__(logger, extra or {})
