import numpy as np
from perlin_noise import PerlinNoise


def generate_terrain(shape, levels, preset="perlin"):
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
        terrain = np.zeros(shape)
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

    terrain -= terrain.min()
    terrain = terrain / terrain.max() * levels
    terrain = np.floor(terrain)
    return terrain
