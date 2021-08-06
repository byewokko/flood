from .drawable import DrawableABC


class Sprite(DrawableABC):
    def step_update(self, r):
        pass

    def continuous_update(self, t):
        pass

    def draw(self, t):
        pass
