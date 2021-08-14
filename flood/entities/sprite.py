from flood.abc.drawable import DrawableABC


class Sprite(DrawableABC):
    def step_update(self, r, inputs=None, **kwargs):
        pass

    def continuous_update(self, t, inputs=None):
        pass

    def draw(self, t, renderer):
        pass
