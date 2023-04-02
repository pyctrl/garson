import abc


class AbstractIpcCell(abc.ABC):

    @abc.abstractmethod
    def get(self):
        raise NotImplementedError

    @abc.abstractmethod
    def put(self, data):
        raise NotImplementedError

    # def delete(self):
    # def post(self):
    # def patch(self):
