import random
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
    # return terrain


class Cell(DrawableABC):
    neighbor_vectors = np.array((
        (0, 1),   # RIGHT
        (-1, 0),  # UP
        (0, -1),  # LEFT
        (1, 0)    # DOWN
    ))
    invert_direction = {
        0: 2,
        1: 3,
        2: 0,
        3: 1
    }

    def __init__(self, grid, coords, terrain_level, water_level):
        self.grid = grid
        self.coords = coords
        self.terrain_level = terrain_level
        self.water_level = water_level
        self.neighbors: Dict[int, Cell] = {}
        self.received_water = [0, 0, 0, 0]
        self.given_water = 0

        # Initiate flow with a tiny number in random direction
        # self.flow = (np.random.random(2) - 0.5)/10
        self.flow = np.zeros(4)
        self.slant = np.zeros(4)
        self.new_flow = np.zeros(4)
        self.flow_vectors = self.neighbor_vectors.copy()

    def initialize(self):
        SLANT_FACTOR = 1
        self.neighbors = self.grid.get_neighbors(self.coords)
        # if 0 in self.neighbors:
        #     slant = self.terrain_level - self.neighbors[0].terrain_level
        #     # self.flow_vectors[0] *= np.array((0, slant*SLANT_FACTOR), dtype=int)
        #     self.flow_vectors[0] *= slant
        # if 1 in self.neighbors:
        #     slant = self.terrain_level - self.neighbors[1].terrain_level
        #     # self.flow_vectors[1] += np.array((-slant * SLANT_FACTOR, 0), dtype=int)
        #     self.flow_vectors[1] *= slant
        # if 2 in self.neighbors:
        #     slant = self.terrain_level - self.neighbors[2].terrain_level
        #     # self.flow_vectors[2] += np.array((0, -slant*SLANT_FACTOR), dtype=int)
        #     self.flow_vectors[2] *= slant
        # if 3 in self.neighbors:
        #     slant = self.terrain_level - self.neighbors[3].terrain_level
        #     # self.flow_vectors[3] += np.array((slant*SLANT_FACTOR, 0), dtype=int)
        #     self.flow_vectors[3] *= slant


        for i, n in self.neighbors.items():
            slant = self.terrain_level - n.terrain_level
            if slant != 0:
                self.slant[i] = slant

    def absolute_level(self):
        return self.water_level + self.terrain_level

    def can_receive(self):
        return 10 - sum(self.received_water)

    def calculate_step_update(self, r):
        if self.water_level <= 0:
            return

        # 1) Distribute water down the slope

        for i, slant in enumerate(self.slant):
            if self.water_level <= self.given_water:
                return
            if slant > 0 and i in self.neighbors:
                amount = min(
                    np.ceil(self.water_level * 0.5 * slant),
                    self.water_level,
                    self.neighbors[i].can_receive()
                )
                self.neighbors[i].received_water[i] += amount
                self.given_water += amount

        # 2) Flow

        if self.water_level > 2:
            average_flow = (
                np.sum([cell.flow for cell in self.neighbors.values()], axis=0) + self.flow
            ) / (len(self.neighbors) + 1)
            # average_flow += 3*self.slant

            for i, flow in enumerate(average_flow):
                if self.water_level <= self.given_water:
                    return
                if flow > 0 and i in self.neighbors:
                    amount = min(
                        np.ceil(self.water_level * 0.1) * flow,
                        self.water_level - 1,
                        self.neighbors[i].can_receive()
                    )
                    # amount = (flow + 1) // 2
                    self.neighbors[i].received_water[i] += amount
                    self.given_water += amount

        # 2) Split the surplus with the lowest neighbor

        neighbor_levels = np.array((
            self.neighbors[0].absolute_level() if 0 in self.neighbors else np.nan,
            self.neighbors[1].absolute_level() if 1 in self.neighbors else np.nan,
            self.neighbors[2].absolute_level() if 2 in self.neighbors else np.nan,
            self.neighbors[3].absolute_level() if 3 in self.neighbors else np.nan,
        ))
        neighbor_difference = self.absolute_level() - neighbor_levels - self.given_water
        direction = int(np.random.choice(np.flatnonzero(neighbor_difference == np.nanmax(neighbor_difference))))
        # direction = int(np.nanargmax(neighbor_difference))

        if neighbor_difference[direction] <= 0:
            return

        water_share = min(
            self.water_level - 1,
            (neighbor_difference[direction] + 0) // 2,
            self.neighbors[direction].can_receive()
        )

        if water_share < 2:
            return

        self.neighbors[direction].received_water[direction] += water_share
        self.given_water += water_share


    def step_update(self, r):
        self.water_level += sum(self.received_water) - self.given_water
        # if self.received_water or self.given_water:
        #     print(f"{tuple(self.coords)}: -{self.given_water} +{self.received_water} ={self.water_level}")
        # self.flow = np.array((
        #     self.received_water[3] - self.received_water[1],
        #     self.received_water[0] - self.received_water[2]
        # ))
        self.flow = np.array((
            self.received_water[0] - self.received_water[2],
            self.received_water[1] - self.received_water[3],
            self.received_water[2] - self.received_water[0],
            self.received_water[3] - self.received_water[1]
        ))
        self.flow[self.slant < 0] = 0
        self.received_water = [0, 0, 0, 0]
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
        terrain_levels=24,
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

        # self.grid[24, 23].water_level += 50
        # self.grid[24, 24].water_level += 50

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
        self.grid[24, 23].water_level += 10
        self.grid[24, 24].water_level += 10
        # self.grid[23, 23].water_level += 10
        # self.grid[23, 24].water_level += 10
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
