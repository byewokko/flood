from typing import Dict
import numpy as np
from OpenGL.GL import *

from flood.abc.drawable import DrawableABC
from .utils import generate_terrain
from ..entities.abc import EntityABC


class Cell(EntityABC, DrawableABC):
    neighbor_vectors = np.array((
        (0, 1),   # RIGHT
        (-1, 0),  # UP
        (0, -1),  # LEFT
        (1, 0)    # DOWN
    ))

    def __init__(self, grid, coords, terrain_level, water_level):
        raise NotImplementedError("Deprecated.")
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
        self.neighbors = self.grid.get_neighbors(self.coords)

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

        # for i, slant in enumerate(self.slant):
        #     if self.water_level <= self.given_water:
        #         return
        #     if slant > 0 and i in self.neighbors:
        #         amount = min(
        #             np.ceil(self.water_level * 0.1 * slant),
        #             self.water_level,
        #             self.neighbors[i].can_receive()
        #         )
        #         self.neighbors[i].received_water[i] += amount
        #         self.given_water += amount

        # 2) Flow

        if self.water_level > 2:
            average_flow = (
                np.sum([cell.flow for cell in self.neighbors.values()], axis=0) + 0.1*self.flow
            ) / (len(self.neighbors) + 0.1)
            # average_flow += 3*self.slant

            for i, flow in enumerate(average_flow):
                if self.water_level <= self.given_water:
                    return
                if flow > 0 and i in self.neighbors and self.slant[i] + 0.1*self.water_level >= 0:
                    amount = min(
                        np.ceil(self.water_level * 0.1) * flow + self.slant[i],
                        self.water_level - 1,
                        self.neighbors[i].can_receive()
                    )
                    # amount = (flow + 1) // 2
                    self.neighbors[i].received_water[i] += amount
                    self.given_water += amount

        # 3) Split the surplus with the lowest neighbor

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


    def step_update(self, r, inputs=None, **kwargs):
        self.water_level += sum(self.received_water) - self.given_water
        self.flow = np.array((
            self.received_water[0] - self.received_water[2],
            self.received_water[1] - self.received_water[3],
            self.received_water[2] - self.received_water[0],
            self.received_water[3] - self.received_water[1]
        ))
        self.flow[self.slant < 0] = 0
        self.received_water = [0, 0, 0, 0]
        self.given_water = 0

    def continuous_update(self, t, inputs=None, **kwargs):
        pass

    def draw(self, t, renderer, **kwargs):
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
        terrain_levels=6,
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
        terrain = generate_terrain(self.shape, self.terrain_levels)
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

    def step_update(self, r, inputs=None, **kwargs):
        # self.grid[24, 23].water_level += 10
        # self.grid[24, 24].water_level += 10
        self.grid[40, 5].water_level += 10
        self.grid[41, 6].water_level += 10
        for cell in self.cells:
            cell.calculate_step_update(r)
        for cell in self.cells:
            cell.step_update(r, None)

    def continuous_update(self, t, inputs=None, **kwargs):
        pass

    def draw(self, t, renderer, **kwargs):
        glPolygonMode(GL_FRONT, GL_FILL)
        for (i, j) in np.ndindex(self.shape):
            glPushMatrix()
            glScale(self.scale, self.scale, 1)
            glTranslate(i, j, 0)
            cell: Cell = self.grid[i, j]
            cell.draw(t, None, water_levels=self.water_levels, terrain_levels=self.terrain_levels)
            glPopMatrix()
