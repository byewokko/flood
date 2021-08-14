import pygame as pg

from .abc import ControllerABC
from ..event import GameEvent


class PyGameKeyboard(ControllerABC):
    _key_to_event = {
        pg.K_UP: GameEvent["player.north"],
        pg.K_LEFT: GameEvent["player.west"],
        pg.K_DOWN: GameEvent["player.south"],
        pg.K_RIGHT: GameEvent["player.east"],
        pg.K_w: GameEvent["player.north"],
        pg.K_a: GameEvent["player.west"],
        pg.K_s: GameEvent["player.south"],
        pg.K_d: GameEvent["player.east"],
        pg.K_ESCAPE: GameEvent["game.quit"],
        pg.K_SEMICOLON: GameEvent["game.command"],
        pg.K_1: GameEvent["game.autoplay"],
    }

    def get_events(self):
        """
        Only one input per turn
        :param game:
        :return:
        """
        game_events = set()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                game_events.add(GameEvent["game.quit"])
            if event.type == pg.KEYDOWN and event.key in self._key_to_event:
                game_events.add(self._key_to_event[event.key])
        return game_events
