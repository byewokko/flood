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


def get_neighbor_coordinates(i, j, direction):
    func = [
        lambda x, y: (x-1, y),
        lambda x, y: (x+1, y),
        lambda x, y: (x, y-1),
        lambda x, y: (x, y+1),
    ]
    return func[direction](i, j)


def make_terrain_grid(shape, levels):
    base = np.tile(np.linspace(0, 2*np.pi, num=shape[0]), (shape[1], 1))
    noise = np.random.random(shape)
    terrain = np.cos(base) * 8 - base.T * 3.6 + noise * 7
    terrain -= terrain.min()
    terrain = terrain / terrain.max() * 6
    return np.floor(terrain)


class Cell(DrawableABC):
    def __init__(self, grid, coords, terrain_level, water_level):
        self.grid = grid
        self.coords = coords
        self.terrain_level = terrain_level
        self.water_level = water_level
        self.neighbors = {
            0: None,
            1: None,
            2: None,
            3: None
        }

        # Initiate flow with a tiny number in random direction
        self.flow = (np.random.random(2) - 0.5)/10

    def initialize(self):
        self.neighbors = self.grid.get_neighbors(self.coords)

    def calculate_step_update(self, r):
        pass

    def step_update(self, r):
        pass

    def continuous_update(self, t):
        pass

    def draw(self, t, color_water, color_terrain):
        # TODO: pass color lambdas
        if self.water_level > 0:
            # draw water
            padding = 0
            water_level = self.water_level
            glColor3f(*(color_water[:2] * np.cos(water_level * np.pi / 2)), 1 - 0.6 * water_level)
            # TODO: draw flow arrow
        else:
            # draw ground
            padding = 0.2
            glColor3f(*(color_terrain * self.terrain_level))

        glBegin(GL_QUADS)
        glVertex2fv((padding, padding))
        glVertex2fv((1 - padding, padding))
        glVertex2fv((1 - padding, 1 - padding))
        glVertex2fv((padding, 1 - padding))
        glEnd()

        glPopMatrix()


class CellularWaterGrid(DrawableABC):
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
        self.terrain_levels = terrain_levels

        self.grid = np.zeros(self.shape, dtype="object")
        self.cells = []
        terrain = make_terrain_grid(self.shape, self.terrain_levels)
        for (i, j) in np.ndindex(self.shape):
            cell = Cell(self, (i, j), terrain[i, j], 0)
            self.grid[i, j] = cell
            self.cells.append(cell)

    def get_neighbors(self, coords):
        neighbors = {}
        # Right
        if coords[1] < self.shape[1] - 1:
            neighbors[0] = self.grid[coords[0], coords[1]+1]
        # Up
        if coords[0] > 0:
            neighbors[1] = self.grid[coords[0]-1, coords[1]]
        # Left
        if coords[1] > 0:
            neighbors[2] = self.grid[coords[0], coords[1]-1]
        # Down
        if coords[1] < self.shape[0] - 1:
            neighbors[3] = self.grid[coords[0]+1, coords[1]]

        return neighbors

    def step_update(self, r):
        for cell in self.cells:
            cell.calculate_step_update(r)
        for cell in self.cells:
            cell.step_update(r)

    def continuous_update(self, t):
        pass

    def draw(self, t):
        glPolygonMode(GL_FRONT, GL_FILL)
        for (i, j) in np.ndindex(self.shape):
            glPushMatrix()
            glScale(self.scale, self.scale, 1)
            glTranslate(i, j, 0)
            cell: Cell = self.grid[i, j]
            cell.draw(t, self.color_water, self.color_ground)
            glPopMatrix()
