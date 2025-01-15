from ..abc import DrawableABC
from .abc import EntityABC
from ..event import GameEvent


class Player(EntityABC, DrawableABC):
    def __init__(self):
        self.x = None
        self.y = None

    def step_update(self, r, events, **kwargs):
        if GameEvent["player.north"] in events:
            self.y -= 1
        if GameEvent["player.west"] in events:
            self.x -= 1
        if GameEvent["player.south"] in events:
            self.y += 1
        if GameEvent["player.east"] in events:
            self.x += 1
        if GameEvent["player.wait"] in events:
            pass

    def continuous_update(self, t, events, **kwargs):
        pass

    def draw(self, t, renderer, **kwargs):
        if self.x is not None and self.y is not None:
            renderer.draw(t, (self.x, self.y), "player")

    def set_coords(self, coords):
        self.x, self.y = coords
