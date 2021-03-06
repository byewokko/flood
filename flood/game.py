import ruamel.yaml
import numpy as np
import pygame as pg

from OpenGL.GL import *

from . import maps, entities, controls
from . import renderer
from .event import GameEvent


class Game:
    def __init__(self, config_file):
        self.Config = {}
        self.load_config(config_file)
        self.display_size = np.array((self.Config["display"]["width"], self.Config["display"]["height"]))
        self.view_size = np.array((self.Config["view"]["width"], self.Config["view"]["height"]))
        self.map_size = (self.Config["map"]["width"], self.Config["map"]["height"])
        self.frame_rate = self.Config["frame rate"]
        self.display_compensation = (1, 1, 1)
        self.round = 0
        self.running = False

        self.Clock = pg.time.Clock()
        self.all_sprites = pg.sprite.Group()
        self.initialize_pygame()
        self.initialize_objects()


    def load_config(self, config_file):
        with open(config_file, "r") as f:
            self.Config = ruamel.yaml.safe_load(f)

    def initialize_pygame(self):
        pg.init()
        pg.display.set_mode(self.display_size, pg.DOUBLEBUF | pg.OPENGL)
        if self.display_size[1] > self.display_size[0]:
            self.display_compensation = (self.display_size[1]/self.display_size[0], 1, 1)
        elif self.display_size[1] < self.display_size[0]:
            self.display_compensation = (1, self.display_size[0]/self.display_size[1], 1)

    def initialize_objects(self):
        self.controller = controls.PyGameKeyboard()
        self.renderer = renderer.Renderer()
        self.grid = maps.FrExWaterGrid(
            shape=self.map_size,
            depth_first_factor=5
        )
        terrain = maps.generate_terrain(
            shape=self.map_size,
            levels=8,
            preset="perlin",
            cave=0.4,
            extra_cave=0.3
        )
        self.grid.set_terrain(terrain)
        self.grid.add_source((10, 20))
        self.grid.add_source((30, 30))
        self.player = entities.Player()
        self.player.set_coords((5, 5))

    def run(self):
        """
        Execute the game loop
        """
        last_update = 0
        self.running = True
        self.waiting_for_player_input = True
        self.autoplay = False
        while self.running:
            t = pg.time.get_ticks() / 1000

            events = self.controller.get_events()
            self.process_events(events)

            if len(events) > 0:
                last_update = t
                self.step_update(t, events)
            elif self.autoplay and t - last_update > 0.1:
                last_update = t
                self.step_update(t, events)

            self.continuous_update(t)

            self.draw(t)

            self.Clock.tick(self.frame_rate)

    def continuous_update(self, t):
        self.grid.continuous_update(t, None)

    def step_update(self, t, events):
        self.round += 1
        self.player.step_update(self.round, events)
        self.grid.step_update(self.round, None)

    def draw(self, t):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()

        # Scale to fit the whole view
        glScale(*(1 / self.view_size), 1)
        # Scale and translate so that 0, 0 is top left
        glScale(1, -1, 1)
        glTranslate(*(-self.view_size), 0)
        # Compensate display ratio distortion
        glScale(*self.display_compensation)

        self.grid.draw(t, self.renderer)
        self.player.draw(t, self.renderer)

        glPopMatrix()
        pg.display.flip()

    def process_events(self, events):
        if GameEvent["game.quit"] in events:
            events.remove(GameEvent["game.quit"])
            self.running = False
        if GameEvent["game.autoplay"] in events:
            events.remove(GameEvent["game.autoplay"])
            self.autoplay = ~self.autoplay
        if GameEvent["game.command"] in events:
            events.remove(GameEvent["game.command"])
            self.get_command_input()

    def get_command_input(self):
        command = input(";;; ")
