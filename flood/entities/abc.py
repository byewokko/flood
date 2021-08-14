import abc


class EntityABC(abc.ABC):
    @abc.abstractmethod
    def step_update(self, r, events, **kwargs):
        """
        Turn-based update
        :param events:
        :param r: Round number
        """
        pass

    @abc.abstractmethod
    def continuous_update(self, t, events, **kwargs):
        """
        Time-based update (animation and transitions)
        :param events:
        :param t: Current time in seconds
        :return:
        """
        pass
