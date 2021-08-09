import numpy as np
from OpenGL.GL import *
from flood.abc.drawable import DrawableABC
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
    terrain = np.sin(base) * 8 - np.cos(base).T * 3.6 + noise * 2
    terrain -= terrain.min()
    terrain = terrain / terrain.max() * 6
    return np.floor(terrain)


class SearchWaterGrid(DrawableABC):
    def __init__(
        self,
        shape,
        water_levels=6,
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
        self.water_levels: int = water_levels
        self.water_grid: np.ndarray = np.zeros(self.shape)
        self.terrain_levels: int = terrain_levels
        self.terrain_grid: np.ndarray = make_terrain_grid(self.shape, self.terrain_levels)
        self._sources = set()
        self._frontier = []
        self._frontier_set = {}
        self._explored = set()

        self.add_source((24, 24))

    def add_source(self, coords):
        self._sources.add(coords)
        self.add_to_frontier(coords, self.water_grid[coords] + self.terrain_grid[coords])

    def add_to_frontier(self, coords, level):
        if (level, coords) in self._explored:
            return
        if (level, coords) in self._frontier_set:
            self._frontier_set[(level, coords)] += 1
            if self._frontier_set[(level, coords)] > 2:
                # prioritize
                # FIXME: this is not working
                heapq.heappush(
                    self._frontier,
                    [
                        level,
                        0.01*np.random.random(),
                        coords
                    ]
                )
            return
        if level in (np.nan, None):
            raise ValueError(f"Invalida value: {level}")
        self._frontier_set[(level, coords)] = 0

        heapq.heappush(
            self._frontier,
            [
                level,
                np.random.random(),
                coords
            ]
        )

    def frontier_pop(self):
        level, _, coords = heapq.heappop(self._frontier)
        self._explored.add((coords, level))
        return coords, level

    def step_update(self, r):
        for _ in range(5):
            self.water_step()

    def water_step(self):
        try:
            coords, frontier_level = self.frontier_pop()
        except IndexError:
            # New source?
            return

        this_level = self.water_grid[coords] + self.terrain_grid[coords]
        if this_level != frontier_level:
            # Old entry
            return

        self.water_grid[coords] += 1
        this_level += 1
        if coords in self._sources:
            self.add_to_frontier(coords, self.water_grid[coords])

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
            for i in range(int(difference)):
                self.add_to_frontier(neighbor, neighbor_level+i)

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
