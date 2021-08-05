import numpy as np
from OpenGL.GL import glScale, glTranslate, glBegin, glVertex2fv, glEnd
from OpenGL.raw.GL.VERSION.GL_1_0 import glPolygonMode, GL_FRONT, GL_FILL, glPushMatrix, glColor3f, glPopMatrix
from OpenGL.raw.GL.VERSION.GL_4_0 import GL_QUADS


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