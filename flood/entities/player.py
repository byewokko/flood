from ..abc import DrawableABC
from .abc import EntityABC


class Player(EntityABC, DrawableABC):
    def __init__(self):
        pass

    def step_update(self, r, events, **kwargs):
        pass

    def continuous_update(self, t, events, **kwargs):
        pass

    def draw(self, t, renderer, **kwargs):
        pass

    def set_coords(self, coords):
        pass
