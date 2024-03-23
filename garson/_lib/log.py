import datetime
import json
import logging


class Encoder(json.JSONEncoder):

    def default(self, obj):
        if hasattr(obj, 'do_dict'):
            return obj.do_dict()
        elif isinstance(obj, (datetime.datetime, datetime.timedelta)):
            return str(obj)
        return super().default(obj)


class LogAdapter(logging.LoggerAdapter):

    # def __init__(self, logger, info, extra=None):
    #     self._info = info
    #     super().__init__(logger, extra or {})

    def process(self, msg, kwargs):
        data = dict(message=msg, **self.extra, **kwargs)
        return json.dumps(data, cls=Encoder), dict()
