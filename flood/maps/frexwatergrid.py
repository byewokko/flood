import numpy as np
from OpenGL.GL import *
import heapq

from flood.abc.drawable import DrawableABC
from utils import generate_terrain


class FrExWaterGrid(DrawableABC):
    """
    Frontier Expansion Water Grid
    ==============================

    Water always expands at the lowest unexpanded levels
    """
    def __init__(
        self,
        shape,
        water_levels=4,
        terrain_levels=6,
        scale=8,
        padding=0.1,
        breadth_first_factor=0.1,
        terrain_preset="perlin"
    ):
        assert len(shape) == 2
        assert shape[0] > 1
        assert shape[1] > 1
        self.scale = scale
        self.padding = padding
        self.color_ground = np.array((0.5, 0.45, 0.45))
        self.color_water = np.array((0.2, 0.3, 1))
        self.shape = shape
        self.water_levels: int = water_levels
        self.water_grid: np.ndarray = np.zeros(self.shape)
        self.terrain_levels: int = terrain_levels
        self.terrain_grid: np.ndarray = generate_terrain(self.shape, self.terrain_levels, terrain_preset)
        self.breadth_first_factor = breadth_first_factor
        self._sources = set()
        self._frontier = []
        self._frontier_set = set()
        self._explored = set()

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

        heapq.heappush(
            self._frontier,
            [
                level,
                np.random.random() + delay,
                coords
            ]
        )

    def frontier_pop(self):
        level, _, coords = heapq.heappop(self._frontier)
        self._frontier_set.remove((level, coords))
        while (coords, level) in self._explored:
            level, _, coords = heapq.heappop(self._frontier)
            self._frontier_set.remove((level, coords))
        self._explored.add((coords, level))
        return coords, level

    def step_update(self, r, n_steps=1):
        for _ in range(n_steps):
            self.water_step(r)

    def water_step(self, r):
        priority = r * self.breadth_first_factor
        try:
            coords, frontier_level = self.frontier_pop()
        except IndexError:
            # New source?
            print(f"index error: frontier_pop")
            return

        this_level = self.water_grid[coords] + self.terrain_grid[coords]

        self.water_grid[coords] += 1
        this_level += 1
        if coords in self._sources:
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
            if neighbor_level is np.nan:
                continue
            difference = this_level - neighbor_level
            # TODO: prioritize expansion down steep slopes
            for i in range(int(difference)):
                self.add_to_frontier(neighbor, neighbor_level+i, priority)

    def continuous_update(self, t):
        pass

    def draw(self, t):
        glPolygonMode(GL_FRONT, GL_FILL)
        for (i, j) in np.ndindex(self.shape):
            if self.water_grid[i, j] > 0:
                padding = 0
                water_level = (self.water_grid[i, j]-1)/self.water_levels
                glColor3f(*(self.color_water[:2] * (1-water_level)), np.cos(water_level * np.pi/2))
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


if __name__ == "__main__":
    import pygame as pg
    window_size = (800, 640)
    view_size = np.array((320, 320))
    display_compensation = (1, window_size[0]/window_size[1], 1)
    frame_rate = 40

    pg.init()
    pg.display.set_mode(window_size, pg.DOUBLEBUF | pg.OPENGL)
    clock = pg.time.Clock()
    grid = FrExWaterGrid(
        shape=(64, 64),
        water_levels=4,
        terrain_levels=4,
        scale=8,
        padding=0.1,
        terrain_preset="perlin4"
    )
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

        grid.step_update(r, n_steps=5)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()

        # Scale to fit the whole view
        glScale(*(1 / view_size), 1)
        # Scale and translate so that 0, 0 is top left
        glScale(1, -1, 1)
        glTranslate(*(-view_size), 0)
        # Compensate display ratio distortion
        glScale(*display_compensation)

        grid.draw(t)

        glPopMatrix()
        pg.display.flip()

        clock.tick(frame_rate)
