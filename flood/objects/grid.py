import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from .drawable import DrawableABC
import heapq


def make_neighbor_grid(shape):
    grid = np.ones(shape, dtype=np.int32) * 4
    grid[:, 0] -= 1
    grid[:, -1] -= 1
    grid[0, :] -= 1
    grid[-1, :] -= 1
    return grid


def get_coordinates(i, j, direction):
    func = [
        lambda x, y: (x-1, y),
        lambda x, y: (x+1, y),
        lambda x, y: (x, y-1),
        lambda x, y: (x, y+1),
    ]
    return func[direction](i, j)


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

        self.water_grid[3, 5] += 12
        self.water_queue = []


    def step_update(self, r):
        self.water_step()

    def water_step(self):
        self.water_grid[3, 5] += 20
        new_grid = np.zeros_like(self.water_grid)
        neighbors_water = np.stack([
            np.pad(self.water_grid, ((1, 0), (0, 0)), constant_values=np.NaN)[:-1, :],  # 0 TOP
            np.pad(self.water_grid, ((0, 1), (0, 0)), constant_values=np.NaN)[1:, :],   # 1 BOTTOM
            np.pad(self.water_grid, ((0, 0), (1, 0)), constant_values=np.NaN)[:, :-1],  # 2 LEFT
            np.pad(self.water_grid, ((0, 0), (0, 1)), constant_values=np.NaN)[:, 1:]    # 3 RIGHT
        ], axis=-1)
        water_queue = []
        for (i, j) in np.ndindex(self.shape):
            heapq.heappush(water_queue, (-self.water_grid[i, j], (i, j)))
        while water_queue:
            neg_lvl, (i, j) = heapq.heappop(water_queue)
            if neg_lvl == 0:
                # No more water to redistribute
                break
            direction = np.nanargmin(neighbors_water[i, j, :])
            if self.water_grid[i, j] > 1:
                share = (self.water_grid[i, j] - neighbors_water[i, j, direction] + 1) // 2
            else:
                share = 0
            new_grid[i, j] += self.water_grid[i, j] - share
            i2, j2 = get_coordinates(i, j, direction)
            new_grid[i2, j2] += share

        self.water_grid = new_grid
        print(f"Total water: {np.sum(self.water_grid)}")

    def continuous_update(self, t):
        pass

    def draw(self, t):
        glPolygonMode(GL_FRONT, GL_FILL)
        for (i, j) in np.ndindex(self.shape):
            if self.water_grid[i, j] > 0:
                padding = 0
                water_level = min(self.water_grid[i, j]/12, 1)
                glColor3f(*(self.color_water[:2] * np.cos(water_level * np.pi/2)), 1 - 0.6*water_level)
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
