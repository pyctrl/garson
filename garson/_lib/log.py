import datetime
import json
import logging


class Encoder(json.JSONEncoder):

    def default(self, obj):
        if hasattr(obj, 'do_dict'):
            return obj.do_dict()
        elif isinstance(obj, (datetime.datetime, datetime.timedelta)):
            return str(obj)
        elif isinstance(obj, type):
            return repr(obj)
        elif isinstance(obj, Exception):
            return repr(obj)
        return super().default(obj)


class LogAdapter(logging.LoggerAdapter):

    # def __init__(self, logger, info, extra=None):
    #     self._info = info
    #     super().__init__(logger, extra or {})

    def process(self, msg, kwargs):
        return json.dumps(dict(message=msg, **self.extra), cls=Encoder), kwargs
