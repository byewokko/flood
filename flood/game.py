import typing
import ruamel.yaml
import numpy as np
import pygame as pg

from OpenGL.GL import *
from OpenGL.GLU import *


class Grid:
    def __init__(self):
        self.size = (20, 20)
        self.grid = np.random.random(self.size)

    def update(self):
        smooth = 3
        self.grid = (smooth*self.grid + np.random.random(self.size)) / (smooth+1)

    def draw(self):
        xspace = 8
        yspace = 8
        width = 1
        height = 1
        color = np.array((0.5, 0, 0.2))
        glPolygonMode(GL_FRONT, GL_FILL)
        for (i, j), value in np.ndenumerate(self.grid):
            glPushMatrix()
            glScale(xspace, yspace, 1)
            glTranslate(i, j, 0)
            glColor3f(*(color*value))

            glBegin(GL_QUADS)
            glVertex2fv((0, 0))
            glVertex2fv((height, 0))
            glVertex2fv((height, width))
            glVertex2fv((0, width))

            glEnd()
            glPopMatrix()


class Game:
    def __init__(self, config_file):
        self.Config = {}
        self.load_config(config_file)
        self.display_size = np.array((self.Config["display"]["width"], self.Config["display"]["height"]))
        self.field_size = np.array((self.Config["field"]["width"], self.Config["field"]["height"]))
        self.frame_rate = self.Config["frame rate"]

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

    def initialize_objects(self):
        self.grid = Grid()

    def run(self):
        """
        Execute the game loop
        """
        while True:
            t = pg.time.get_ticks() / 1000
            # get input
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    return

            # update all the sprites
            # self.all_sprites.update()
            self.grid.update()

            # draw the scene
            # self.Screen.fill(pg.Color(63, 0, 31))
            # dirty = self.all_sprites.draw(self.Screen)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glPushMatrix()

            # Compensate display ratio
            glScale(self.display_size[1]/self.display_size[0], 1, 1)
            # Scale to fit the whole field
            glScale(*(1/self.field_size), 1)
            glRotate(5*t % 360, 0, 0, 1)
            glTranslate(-100, -100, 0)
            self.grid.draw()
            glPopMatrix()
            pg.display.flip()
            # pg.display.update(dirty)

            # cap the framerate at 40fps. Also called 40HZ or 40 times per second.
            self.Clock.tick(self.frame_rate)
