import os

from garson.ipc.cells import base


class FileAbstractIpcCell(base.AbstractIpcCell):

    def __init__(self, path: str):
        self._path = path

    def get(self):
        with open(self._path, "r") as f:
            return f.read()

    def put(self, data: str):
        new_path = self._path + ".tmp"
        with open(new_path, "w") as f:
            f.write(data)
        os.rename(new_path, self._path)
