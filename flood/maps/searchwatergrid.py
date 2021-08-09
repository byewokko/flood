import numpy as np
from perlin_noise import PerlinNoise
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


def make_terrain_grid(shape, levels, preset):
    if preset == "bumps1":
        base = np.tile(np.linspace(0, 2*np.pi, num=shape[0]), (shape[1], 1))
        noise = np.random.random(shape)
        terrain = base*np.sin(2*base) * 1 - base.T+np.cos(1.5*base).T * 3 + noise * 3
    elif preset == "well":
        base = np.tile(np.linspace(0, 2 * np.pi, num=shape[0]), (shape[1], 1))
        noise = np.random.random(shape)
        terrain = base * np.sin(base) - base.T * 3 + noise * 3
        x = shape[0] // 8
        y = shape[1] // 8
        terrain[3*x:5*x, 3*y:5*y] = terrain.min() - 2
    elif preset == "walls":
        terrain = np.zeros(shape)
        noise_gen = PerlinNoise(octaves=8)
        terrain = np.reshape([
            noise_gen([x/shape[0], y/shape[1]])
            for (x, y)
            in np.ndindex(shape)
        ], shape) * 4
        x = shape[0] // 8
        y = shape[1] // 8
        terrain[3*x, 3*y:5*y] = 5
        terrain[5*x, 3*y:5*y] = 5
        terrain[3*x:5*x, 3*y] = 5
        terrain[3*x:5*x, 5*y] = 5
        terrain[:, 1*y] = -1
        terrain[1*x, :] = -1
        terrain[:, 4*y] = 4
        terrain[4*x, :] = 4
    elif preset == "perlin":
        noise_gen = PerlinNoise(octaves=8)
        terrain = np.reshape([
            noise_gen([x/shape[0], y/shape[1]])
            for (x, y)
            in np.ndindex(shape)
        ], shape)

    terrain -= terrain.min()
    terrain = terrain / terrain.max() * levels
    terrain = np.floor(terrain)
    return terrain


class SearchWaterGrid(DrawableABC):
    def __init__(
        self,
        shape,
        water_levels=4,
        terrain_levels=6,
        scale=8,
        padding=0.1
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
        self.terrain_grid: np.ndarray = make_terrain_grid(self.shape, self.terrain_levels, "walls")
        self._sources = set()
        self._frontier = []
        self._frontier_set = set()
        self._explored = set()

        self.add_source((10, 20))
        # self.add_source((40, 5))
        # self.add_source((64-4, 64-8))
        # self.add_source((28, 20))

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

    def step_update(self, r):
        for _ in range(6):
            self.water_step(r)

    def water_step(self, r):
        priority = r*0.1
        try:
            coords, frontier_level = self.frontier_pop()
        except IndexError:
            # New source?
            print(f"index error: frontier_pop")
            return

        this_level = self.water_grid[coords] + self.terrain_grid[coords]
        # if this_level != frontier_level:
        #     # Old entry
        #     return

        self.water_grid[coords] += 1
        this_level += 1
        if coords in self._sources:
            self.add_to_frontier(coords, self.water_grid[coords]+1, priority)

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
