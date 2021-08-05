import ruamel.yaml
import numpy as np
import pygame as pg

from OpenGL.GL import *

from .objects.flashgrid import Grid


class Game:
    def __init__(self, config_file):
        self.Config = {}
        self.load_config(config_file)
        self.display_size = np.array((self.Config["display"]["width"], self.Config["display"]["height"]))
        self.field_size = np.array((self.Config["field"]["width"], self.Config["field"]["height"]))
        self.frame_rate = self.Config["frame rate"]
        self.display_compensation = (1, 1, 1)
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
        print(self.display_size)
        if self.display_size[1] > self.display_size[0]:
            self.display_compensation = (self.display_size[1]/self.display_size[0], 1, 1)
        elif self.display_size[1] < self.display_size[0]:
            self.display_compensation = (1, self.display_size[0]/self.display_size[1], 1)

    def initialize_objects(self):
        self.grid = Grid()

    def run(self):
        """
        Execute the game loop
        """
        self.running = True
        while self.running:
            t = pg.time.get_ticks() / 1000

            self.get_inputs(t)

            self.update(t)

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

    def update(self, t):
        self.grid.update()

    def draw(self, t):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()

        # Scale to fit the whole field
        glScale(*(1 / self.field_size), 1)
        # Translate so that 0, 0 is bottom left
        glTranslate(*(-self.field_size), 0)
        # Compensate display ratio distortion
        glScale(*self.display_compensation)

        self.grid.draw()

        glPopMatrix()
        pg.display.flip()
