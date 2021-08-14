import abc


class ControllerABC(abc.ABC):
    @abc.abstractmethod
    def get_events(self):
        pass
