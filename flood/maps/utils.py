import numpy as np
from perlin_noise import PerlinNoise
from pyperlin import FractalPerlin2D
# TODO: custom perlin implementation using only numpy


def generate_terrain(shape, levels, preset="perlin", cave=None, extra_cave=None):
    normalize = True
    if preset == "bumps":
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
        noise_gen = PerlinNoise(octaves=8)
        terrain = np.reshape([
            noise_gen([x/shape[0], y/shape[1]])
            for (x, y)
            in np.ndindex(shape)
        ], shape) * 4
        x = shape[0] // 8
        y = shape[1] // 8
        terrain[3*x, 3*y:5*y+1] = 5
        terrain[5*x, 3*y:5*y+1] = 5
        terrain[3*x:5*x+1, 3*y] = 5
        terrain[3*x:5*x+1, 5*y] = 5
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
    elif preset == "perlin4":
        resolutions = [(2 ** i, 2 ** i) for i in range(1, 7)]  # for lacunarity = 2.0
        factors = [.9 ** i for i in range(6)]  # for persistence = 0.5
        terrain = FractalPerlin2D((1, *shape), resolutions, factors)().cpu().numpy()[0]

    elif preset == "checker_terrain":
        noise_gen = PerlinNoise(octaves=3)
        terrain = np.reshape([
            noise_gen([x / shape[0], y / shape[1]])
            for (x, y)
            in np.ndindex(shape)
        ], shape)*2
        noise = np.zeros(shape)
        for (x, y) in np.ndindex(shape):
            noise[x, y] = (x+y)%2
        terrain += noise
    elif preset == "checker":
        terrain = np.ones(shape) * 2
        for (x, y) in np.ndindex(shape):
            terrain[x, y] += (x+y)%2
        normalize = False

    if normalize:
        terrain -= terrain.min()
        terrain = terrain / terrain.max()
        if cave:
            terrain[terrain > (1 - cave)] = np.nan
        terrain = terrain / np.nanmax(terrain) * levels
        terrain = np.floor(terrain)
    if extra_cave:
        noise_gen = PerlinNoise(octaves=8)
        cave_profile = np.reshape([
            noise_gen([x / shape[0], y / shape[1]])
            for (x, y)
            in np.ndindex(shape)
        ], shape)
        cave_profile -= cave_profile.min()
        cave_profile = cave_profile / cave_profile.max()
        terrain[cave_profile > (1 - extra_cave)] = np.nan

    return terrain
