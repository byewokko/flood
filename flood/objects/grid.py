import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from .drawable import DrawableABC


def make_neighbor_grid(shape):
    grid = np.ones(shape, dtype=np.int32) * 5
    grid[:, 0] -= 1
    grid[:, -1] -= 1
    grid[0, :] -= 1
    grid[-1, :] -= 1
    return grid


class Grid(DrawableABC):
    def __init__(self, shape, scale=8, padding=0.1):
        assert len(shape) == 2
        assert shape[0] > 1
        assert shape[1] > 1
        self.shape = shape
        self.water_grid = np.zeros(self.shape)
        self.neighbor_grid = make_neighbor_grid(self.shape)
        self.scale = scale
        self.padding = padding
        self.color_ground = np.array((0.15, 0, 0.05))
        self.color_water = np.array((0.3, 0.4, 1))

    def step_update(self, r):
        self.water_step()

    def water_step(self):
        self.water_grid[3, 5] += 1
        new_grid = np.zeros_like(self.water_grid)
        # for (i, j) in np.ndindex(self.shape):
        #     # Sum differences with neighboring cells
        neighbors = np.pad(self.water_grid, ((1, 0), (0, 0)), constant_values=0)[:-1, :] \
            + np.pad(self.water_grid, ((0, 1), (0, 0)), constant_values=0)[1:, :] \
            + np.pad(self.water_grid, ((0, 0), (1, 0)), constant_values=0)[:, :-1] \
            + np.pad(self.water_grid, ((0, 0), (0, 1)), constant_values=0)[:, 1:]
        new_grid = (self.water_grid + neighbors) / self.neighbor_grid
        self.water_grid = new_grid
        print(f"Total water: {np.sum(self.water_grid)}")

    def continuous_update(self, t):
        pass

    def draw(self, t):
        glPolygonMode(GL_FRONT, GL_FILL)
        for (i, j) in np.ndindex(self.shape):
            if self.water_grid[i, j] > 0.1:
                padding = 0
                water_level = min(self.water_grid[i, j], 1)
                glColor3f(*(self.color_water[:2] * np.sin(water_level * np.pi/2)), 0.4 + 0.6*water_level)
            else:
                padding = self.padding
                glColor3f(*self.color_ground)
            glPushMatrix()
            glScale(self.scale, self.scale, 1)
            glTranslate(i, j, 0)

            glBegin(GL_QUADS)
            glVertex2fv((padding, padding))
            glVertex2fv((1-padding, padding))
            glVertex2fv((1-padding, 1-padding))
            glVertex2fv((padding, 1-padding))
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
