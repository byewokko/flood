import math

import numpy as np
from OpenGL.GL import *
import heapq

from ..abc.drawable import DrawableABC
from ..entities.abc import EntityABC
from flood.renderer import Renderer
from .utils import generate_terrain


class FrExWaterGrid(EntityABC, DrawableABC):
    """
    Frontier Expansion Water Grid
    ==============================

    Water always expands at the lowest unexpanded levels
    """
    def __init__(
        self,
        shape,
        depth_first_factor=1
    ):
        assert len(shape) == 2
        assert shape[0] > 1
        assert shape[1] > 1
        self.color_ground = np.array((0.5, 0.45, 0.45))
        self.color_water = np.array((0.3, 0.4, 1))
        self.color_wave = np.array((0.7, 0.7, 1))
        self.shape = shape
        self.water_levels: int = 1
        self.water_grid: np.ndarray = np.zeros(self.shape)
        self.terrain_levels: int = 1
        self.terrain_grid: np.ndarray = np.zeros(self.shape)
        self.depth_first_factor = depth_first_factor
        self.total_steps = 0
        self._sources = set()
        self._frontier = []
        self._frontier_set = set()
        self._explored = set()

    def set_terrain(self, terrain):
        assert terrain.shape == self.shape
        self.terrain_grid = terrain
        self.terrain_levels = int(np.nanmax(terrain) - np.nanmin(terrain)) + 1
        self.water_levels = self.terrain_levels + 2

    def add_source(self, coords):
        self._sources.add(coords)
        self.add_to_frontier(coords, self.water_grid[coords] + self.terrain_grid[coords])

    def add_to_frontier(self, coords, level, delay=0):
        if (level, coords) in self._explored:
            return
        if (level, coords) in self._frontier_set:
            return
        if level in (np.nan, None):
            raise ValueError(f"Invalid value: {level}")
        self._frontier_set.add((level, coords))

        # Lower value = higher priority
        queue_value = level * (self.depth_first_factor + np.random.random() * delay)


        heapq.heappush(
            self._frontier,
            [
                queue_value,
                level,
                coords
            ]
        )

    def frontier_pop(self):
        _, level, coords = heapq.heappop(self._frontier)
        self._frontier_set.remove((level, coords))
        while (coords, level) in self._explored:
            _, level, coords = heapq.heappop(self._frontier)
            self._frontier_set.remove((level, coords))
        self._explored.add((coords, level))
        return coords, level

    def step_update(self, r, events, **kwargs):
        n_steps = 5
        for _ in range(n_steps):
            self.water_step(r)
        if r % 50 == 0:
            print(f"Round {r}, Water updates: {self.total_steps}")

    def water_step(self, r):
        self.total_steps += 1
        priority = r
        coords = None
        while coords is None:
            try:
                coords, frontier_level = self.frontier_pop()
            except IndexError:
                print(f"index error: frontier is empty")
                coords = None
                return

            this_level = self.water_grid[coords] + self.terrain_grid[coords]
            if np.isnan(this_level):
                coords = None

        self.water_grid[coords] += 1
        this_level += 1
        if coords in self._sources and this_level < self.terrain_levels+2:  # water shouldn't rise above max_terrain+2
            self.add_to_frontier(coords, this_level+1, priority)

        # add neighbors
        for neighbor in [
            (coords[0] - 1, coords[1]),
            (coords[0] + 1, coords[1]),
            (coords[0], coords[1] - 1),
            (coords[0], coords[1] + 1)
        ]:
            if not ((0 <= neighbor[0] < self.shape[0]) and (0 <= neighbor[1] < self.shape[1])):
                continue
            neighbor_level = self.water_grid[neighbor] + self.terrain_grid[neighbor]
            if np.isnan(neighbor_level):
                continue
            difference = this_level - neighbor_level
            # TODO: prioritize expansion down steep slopes
            neighbor_priority = -1 if difference > 1 else priority
            for i in range(int(difference)):
                self.add_to_frontier(neighbor, neighbor_level+i, neighbor_priority)

    def continuous_update(self, t, events, **kwargs):
        pass

    def draw(self, t, renderer: Renderer, **kwargs):
        glPolygonMode(GL_FRONT, GL_FILL)
        # glLineWidth(0.1)
        for coords in np.ndindex(self.shape):
            (i, j) = coords
            if np.isnan(self.terrain_grid[i, j]):
                continue
            if (i, j) in self._sources:
                water_level = (self.water_grid[i, j] - 1)/self.water_levels
                renderer.draw(t, coords, "water", water_level=water_level)
                renderer.draw(t, coords, "water_source")
            elif self.water_grid[i, j] > 0:
                water_level = (self.water_grid[i, j] - 1)/self.water_levels
                total_level = (
                    self.terrain_grid[i, j] + self.water_grid[i, j] - 1
                ) / (self.terrain_levels + 2)  # water shouldn't rise above max_terrain+2
                renderer.draw(t, coords, "water", water_level=water_level)
                renderer.draw(t, coords, "water_wave", total_level=total_level)
            else:
                terrain_level = (self.terrain_grid[i, j] - 1)/self.terrain_levels
                renderer.draw(t, coords, "ground", terrain_level=terrain_level)


if __name__ == "__main__":
    import pygame as pg
    window_size = (800, 640)
    view_size = np.array((320, 320))
    display_compensation = (1, window_size[0]/window_size[1], 1)
    frame_rate = 40

    pg.init()
    pg.display.set_mode(window_size, pg.DOUBLEBUF | pg.OPENGL)
    clock = pg.time.Clock()
    renderer = Renderer()
    shape = (64, 64)
    grid = FrExWaterGrid(
        shape=shape,
        depth_first_factor=5
    )
    terrain = generate_terrain(
        shape=shape,
        levels=8,
        preset="perlin",
        cave=0.4,
        extra_cave=0.3
    )
    grid.set_terrain(terrain)
    grid.add_source((10, 20))
    grid.add_source((30, 30))

    stop = False
    r = 0  # round_number
    while not stop:
        t = pg.time.get_ticks() / 1000
        r += 1

        for event in pg.event.get():
            if event.type == pg.QUIT:
                stop = True
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                stop = True

        grid.step_update(r, None)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()

        # Scale to fit the whole view
        glScale(*(1 / view_size), 1)
        # Scale and translate so that 0, 0 is top left
        glScale(1, -1, 1)
        glTranslate(*(-view_size), 0)
        # Compensate display ratio distortion
        glScale(*display_compensation)

        grid.draw(t, None)

        glPopMatrix()
        pg.display.flip()

        clock.tick(frame_rate)
