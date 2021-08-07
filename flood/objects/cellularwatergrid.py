from typing import Dict

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
    neighbor_vectors = np.array((
        (0, 1),
        (-1, 0),
        (0, -1),
        (1, 0)
    ))

    def __init__(self, grid, coords, terrain_level, water_level):
        self.grid = grid
        self.coords = coords
        self.terrain_level = terrain_level
        self.water_level = water_level
        self.neighbors: Dict[int, Cell] = {}
        self.slant = [0, 0]
        self.received_water = 0
        self.given_water = 0

        # Initiate flow with a tiny number in random direction
        self.flow = (np.random.random(2) - 0.5)/10
        self.new_flow = np.zeros(2)

    def initialize(self):
        self.neighbors = self.grid.get_neighbors(self.coords)
        slant = np.zeros(4)
        slant[:] = np.nan
        primary_slant = {}
        if 0 in self.neighbors:
            slant[0] = self.terrain_level - self.neighbors[0].terrain_level
            primary_slant[0] = np.array((0, slant[0]))
        if 1 in self.neighbors:
            slant[1] = self.terrain_level - self.neighbors[1].terrain_level
            primary_slant[1] = np.array((-slant[1], 0))
        if 2 in self.neighbors:
            slant[2] = self.terrain_level - self.neighbors[2].terrain_level
            primary_slant[2] = np.array((0, -slant[2]))
        if 3 in self.neighbors:
            slant[3] = self.terrain_level - self.neighbors[3].terrain_level
            primary_slant[3] = np.array((slant[3], 0))
        self.slant = slant
        self.slant_vector = np.sum((
            primary_slant.get(0, np.array((0, 0))),
            primary_slant.get(2, np.array((0, 0))),
            primary_slant.get(1, np.array((0, 0))),
            primary_slant.get(3, np.array((0, 0)))
        )) / 2
        self.primary_slant_vector = primary_slant[int(np.nanargmax(np.abs(slant)))]

    def calculate_step_update(self, r):
        if self.water_level <= 0:
            return
        # Average flow
        self.new_flow = (np.sum(list(map(lambda c: c.flow, self.neighbors.values()))) + self.flow) / 5
        self.new_flow += self.slant_vector
        flow_dot_prod = np.dot(self.new_flow, self.neighbor_vectors.T)
        directions = np.argsort(flow_dot_prod)
        for d in directions:
            if (direction := int(d)) in self.neighbors:
                break
        water_amount = int(self.water_level * np.abs(self.new_flow[(direction + 1) % 2]))
        water_amount = min(self.water_level, water_amount)
        self.given_water += water_amount
        self.neighbors[direction].received_water += water_amount
        self.new_flow[(direction + 1) % 2] = water_amount * (-1)**(direction in (1, 2))
        self.new_flow[(direction) % 2] = 0

    def step_update(self, r):
        self.water_level += self.received_water - self.given_water
        self.flow = self.new_flow
        self.received_water = 0
        self.given_water = 0

    def continuous_update(self, t):
        pass

    def draw(self, t, color_water, color_terrain, water_levels, terrain_levels):
        # TODO: pass color lambdas
        if self.water_level > 0:
            # draw water
            padding = 0
            water_level = self.water_level/water_levels
            glColor3f(*(color_water[:2] * np.cos(water_level * np.pi / 2)), 1 - 0.6 * water_level)
            # TODO: draw flow arrow
        else:
            # draw ground
            padding = 0.2
            glColor3f(*(color_terrain * self.terrain_level/terrain_levels))

        glBegin(GL_QUADS)
        glVertex2fv((padding, padding))
        glVertex2fv((1 - padding, padding))
        glVertex2fv((1 - padding, 1 - padding))
        glVertex2fv((padding, 1 - padding))
        glEnd()


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
        for cell in self.cells:
            cell.initialize()

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
        if coords[0] < self.shape[0] - 1:
            neighbors[3] = self.grid[coords[0]+1, coords[1]]

        return neighbors

    def step_update(self, r):
        self.grid[3, 5].water_level = 6
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
            cell.draw(
                t,
                self.color_water,
                self.color_ground,
                water_levels=self.water_levels,
                terrain_levels=self.terrain_levels
            )
            glPopMatrix()
