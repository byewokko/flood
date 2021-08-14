from flood.abc import DrawableABC


class Player(DrawableABC):
    def step_update(self, r, inputs=None, **kwargs):
        pass

    def continuous_update(self, t, inputs=None, **kwargs):
        pass

    def draw(self, t, renderer, **kwargs):
        pass

    def set_coords(self, coords):
        pass
