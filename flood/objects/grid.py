import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from .drawable import DrawableABC


class Grid(DrawableABC):
    def __init__(self, shape, padding=0.1, scale=8):
        assert len(shape) == 2
        assert shape[0] > 1
        assert shape[1] > 1
        self.shape = shape
        self.base_grid = np.random.random(self.shape)
        self.scale = scale
        self.padding = padding
        self.color = np.array((0.5, 0, 0.2))

    def step_update(self, r):
        pass

    def continuous_update(self, t):
        pass

    def draw(self, t):
        glPolygonMode(GL_FRONT, GL_FILL)
        glColor3f(*self.color)
        for (i, j) in np.ndindex(self.shape):
            glPushMatrix()
            glScale(self.scale, self.scale, 1)
            glTranslate(i, j, 0)

            glBegin(GL_QUADS)
            glVertex2fv((0, 0))
            glVertex2fv((1-self.padding, 0))
            glVertex2fv((1-self.padding, 1-self.padding))
            glVertex2fv((0, 1-self.padding))
            glEnd()

            glPopMatrix()


if __name__ == "__main__":
    import pygame as pg
    pg.init()
    pg.display.set_mode((800, 640), pg.DOUBLEBUF | pg.OPENGL)
    display_compensation = (1, 800/640, 1)
    clock = pg.time.Clock()
    grid = Grid()

    stop = False
    while not stop:
        t = pg.time.get_ticks() / 1000

        for event in pg.event.get():
            if event.type == pg.QUIT:
                stop = True
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                stop = True

        grid.update(t)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()

        # Scale to fit the whole field
        glScale(1/100, 1/100, 1)
        # Translate so that 0, 0 is bottom left
        glTranslate(-100, -100, 0)
        # Compensate display ratio distortion
        glScale(*display_compensation)

        grid.draw(t)

        glPopMatrix()
        pg.display.flip()

        clock.tick(40)
