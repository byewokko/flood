import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *


class Grid:
    def __init__(self):
        self.size = (30, 20, 3)
        self.grid = np.random.random(self.size)
        self.xspacing = 8
        self.yspacing = 8
        self.width_ratio = 1
        self.height_ratio = 1
        self.color = np.array((0.5, 0, 0.2))
        self.flash_color = np.array((0.5, 0.3, 0.3))
        self.color_smoothing = 3

    def update(self, t):
        flash = (np.random.random(self.size) > 0.999) * self.flash_color
        self.grid = (
            (self.color_smoothing*self.grid + np.random.random(self.size) * self.color) / (self.color_smoothing+1)
        ) + flash

    def draw(self, t):
        glPolygonMode(GL_FRONT, GL_FILL)
        for (i, j) in np.ndindex(self.size[:2]):
            glPushMatrix()
            glScale(self.xspacing, self.yspacing, 1)
            glTranslate(i, j, 0)
            glRotate(5*(12*t + 5*i + 2*j) % 360, 0, 0, 1)
            glColor3f(*self.grid[i, j, :])

            glBegin(GL_QUADS)
            glVertex2fv((0, 0))
            glVertex2fv((self.height_ratio, 0))
            glVertex2fv((self.height_ratio, self.width_ratio))
            glVertex2fv((0, self.width_ratio))
            glEnd()

            glPopMatrix()
