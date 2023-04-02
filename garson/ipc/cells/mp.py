import multiprocessing as mp

from garson.ipc.cells import base


class MpValueAbstractIpcCell(base.AbstractIpcCell):

    def __init__(self, typecode_or_type, *args, lock=True):
        self._value = mp.Value(typecode_or_type, *args, lock=lock)

    def get(self):
        with self._value.get_lock():
            return self._value.value

    def put(self, data):
        with self._value.get_lock():
            self._value.value = data
