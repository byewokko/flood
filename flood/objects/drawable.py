import abc


class DrawableABC(abc.ABC):
    @abc.abstractmethod
    def step_update(self, r):
        """
        Turn-based update
        :param r: Round number
        """
        pass

    @abc.abstractmethod
    def continuous_update(self, t):
        """
        Time-based update (animation and transitions)
        :param t: Current time in seconds
        :return:
        """
        pass

    @abc.abstractmethod
    def draw(self, t, *args, **kwargs):
        """
        Draw graphics
        :param t: Current time in seconds
        :return:
        """
        pass

