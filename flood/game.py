import ruamel.yaml
import numpy as np
import pygame as pg

from OpenGL.GL import *

from . import maps, entities
from . import renderer


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
        while self.running:
            t = pg.time.get_ticks() / 1000

            self.get_inputs(t)

            if t - last_update > 0.1:
                last_update = t
                self.step_update(t)

            self.continuous_update(t)

            self.draw(t)

            self.Clock.tick(self.frame_rate)

    def get_inputs(self, t):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.running = False
                return

    def continuous_update(self, t):
        self.grid.continuous_update(t)

    def step_update(self, t):
        self.round += 1
        self.grid.step_update(self.round)

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

        glPopMatrix()
        pg.display.flip()
