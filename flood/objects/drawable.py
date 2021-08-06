import abc


class DrawableABC(abc.ABC):
    def step_update(self, r):
        """
        Turn-based update
        :param r: Round number
        """
        raise NotImplementedError()

    def continuous_update(self, t):
        """
        Time-based update (animation and transitions)
        :param t: Current time in seconds
        :return:
        """
        raise NotImplementedError()

    def draw(self, t):
        """
        Draw graphics
        :param t: Current time in seconds
        :return:
        """
        raise NotImplementedError()

