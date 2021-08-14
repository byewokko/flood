import abc


class EntityABC(abc.ABC):
    @abc.abstractmethod
    def step_update(self, r, inputs=None, **kwargs):
        """
        Turn-based update
        :param inputs:
        :param r: Round number
        """
        pass

    @abc.abstractmethod
    def continuous_update(self, t, inputs=None, **kwargs):
        """
        Time-based update (animation and transitions)
        :param inputs:
        :param t: Current time in seconds
        :return:
        """
        pass
