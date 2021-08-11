import numpy as np
from OpenGL.GL import *
from flood.abc.drawable import DrawableABC
import heapq

from .utils import generate_terrain


def get_neighbor_coordinates(i, j, direction):
    func = [
        lambda x, y: (x-1, y),
        lambda x, y: (x+1, y),
        lambda x, y: (x, y-1),
        lambda x, y: (x, y+1),
    ]
    return func[direction](i, j)


class SimpleWaterGrid(DrawableABC):
    def __init__(
        self,
        shape,
        water_levels=12,
        terrain_levels=12,
        scale=8,
        padding=0.2
    ):
        assert len(shape) == 2
        assert shape[0] > 1
        assert shape[1] > 1
        self.scale = scale
        self.padding = padding
        self.color_ground = np.array((0.5, 0.45, 0.45))
        self.color_water = np.array((0.3, 0.4, 1))
        self.shape = shape
        self.water_levels = water_levels
        self.water_grid = np.zeros(self.shape)
        self.terrain_levels = terrain_levels
        self.terrain_grid = generate_terrain(self.shape, self.terrain_levels)

        self.water_grid[3, 5] = 0


    def step_update(self, r):
        self.water_step()

    def water_step(self):
        self.water_grid[3, 5] += 5
        new_grid = np.zeros_like(self.water_grid)
        total_levels = self.water_grid + self.terrain_grid
        neighbors_levels = np.stack([
            np.pad(total_levels, ((1, 0), (0, 0)), constant_values=np.NaN)[:-1, :],  # 0 TOP
            np.pad(total_levels, ((0, 1), (0, 0)), constant_values=np.NaN)[1:, :],   # 1 BOTTOM
            np.pad(total_levels, ((0, 0), (1, 0)), constant_values=np.NaN)[:, :-1],  # 2 LEFT
            np.pad(total_levels, ((0, 0), (0, 1)), constant_values=np.NaN)[:, 1:]    # 3 RIGHT
        ], axis=-1)
        water_queue = []
        for (i, j) in np.ndindex(self.shape):
            heapq.heappush(water_queue, (-self.water_grid[i, j], (i, j)))
        while water_queue:
            neg_lvl, (i, j) = heapq.heappop(water_queue)
            if neg_lvl == 0:
                # No more water to redistribute
                break
            direction = np.nanargmin(neighbors_levels[i, j, :])
            i2, j2 = get_neighbor_coordinates(i, j, direction)
            share = min(
                (total_levels[i, j] - total_levels[i2, j2]) // 2,
                self.water_grid[i, j]
            )
            new_grid[i, j] += self.water_grid[i, j] - share
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
                water_level = min(self.water_grid[i, j]/self.water_levels, 1)
                glColor3f(*(self.color_water[:2] * np.cos(water_level * np.pi/2)), 1 - 0.6*water_level)
            else:
                padding = self.padding
                glColor3f(*(self.color_ground * self.terrain_grid[i, j]/self.terrain_levels))
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
