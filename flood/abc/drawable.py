import abc


class DrawableABC(abc.ABC):
    @abc.abstractmethod
    def draw(self, t, renderer, **kwargs):
        """
        Draw graphics
        :param renderer:
        :param t: Current time in seconds
        :return:
        """
        pass

