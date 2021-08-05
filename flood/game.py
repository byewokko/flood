import typing
import ruamel.yaml
import numpy as np
import pygame as pg

from OpenGL.GL import *
from OpenGL.GLU import *


class Grid:
    def __init__(self):
        self.grid = np.random.random((1, 1))

    def draw(self):
        yspace = 32
        xspace = 32
        height = 0.8
        width = 0.8
        glPolygonMode(GL_FRONT, GL_FILL)
        glColor3f(0.12, 0, 0.06)
        glBegin(GL_QUADS)
        for (i, j), value in np.ndenumerate(self.grid):
            glVertex2fv((i*yspace, j*xspace))
            glVertex2fv(((i+height)*yspace, j*xspace))
            glVertex2fv(((i+height)*yspace, (j+width)*xspace))
            glVertex2fv((i*yspace, (j+width)*xspace))
        glEnd()


class Game:
    def __init__(self, config_file):
        self.Config = {}
        self.load_config(config_file)
        self.Screen: typing.Optional[pg.Surface] = None
        self.ScreenRect = pg.Rect(0, 0, 800, 800)
        self.Clock = pg.time.Clock()
        self.all_sprites = pg.sprite.Group()
        self.initialize_pygame()
        self.initialize_objects()


    def load_config(self, config_file):
        with open(config_file, "r") as f:
            self.Config = ruamel.yaml.safe_load(f)

    def initialize_pygame(self):
        pg.init()
        display = (800, 640)
        pg.display.set_mode(display, pg.DOUBLEBUF | pg.OPENGL)

    def initialize_objects(self):
        self.grid = Grid()

    def run(self):
        """
        Execute the game loop
        """
        while True:
            # get input
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    return

            # update all the sprites
            # self.all_sprites.update()

            # draw the scene
            # self.Screen.fill(pg.Color(63, 0, 31))
            # dirty = self.all_sprites.draw(self.Screen)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            self.grid.draw()
            pg.display.flip()
            # pg.display.update(dirty)

            # cap the framerate at 40fps. Also called 40HZ or 40 times per second.
            self.Clock.tick(40)
