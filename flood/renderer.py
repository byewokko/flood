import numpy as np
from OpenGL.GL import *


class Sprite:
    terrain_range = None
    water_range = None

    @classmethod
    def configure(cls, terrain_range=None):
        if terrain_range is not None:
            cls.terrain_range = terrain_range
            cls.water_range = terrain_range + 2

    @classmethod
    def draw(cls, *args, **kwargs):
        raise NotImplementedError()


class Ground(Sprite):
    color = np.array((0.5, 0.45, 0.45))
    padding = 0.1
    vertices = [
        (padding, padding),
        (1 - padding, padding),
        (1 - padding, 1 - padding),
        (padding, 1 - padding)
    ]

    @classmethod
    def configure(cls, padding=None):
        if padding is not None:
            cls.padding = padding

    @classmethod
    def draw(cls, *, terrain_level):
        glPolygonMode(GL_FRONT, GL_FILL)
        glColor3f(*(cls.color * terrain_level))
        glBegin(GL_QUADS)
        for pair in cls.vertices:
            glVertex2fv(pair)
        glEnd()


class Water(Sprite):
    color_water = np.array((0.3, 0.4, 1))
    color_wave = np.array((0.7, 0.7, 1))
    tile_vertices = [
        (0, 0),
        (1, 0),
        (1, 1),
        (0, 1)
    ]
    wave_vertices = [
        (0, 0.35),
        (0.7, 0.15),
        (0.3, 0.85),
        (1, 0.65)
    ]

    @classmethod
    def configure(cls, padding=None):
        if padding is not None:
            cls.padding = padding

    @classmethod
    def draw(cls, *, water_level, total_level):
        glPolygonMode(GL_FRONT, GL_FILL)
        # glColor3f(*(cls.color_water * water_level / cls.terrain_range))
        glColor3f(*(cls.color_water[:2] * (1 - water_level)), np.cos(water_level * np.pi / 2))
        glBegin(GL_QUADS)
        for pair in cls.tile_vertices:
            glVertex2fv(pair)
        glEnd()
        glColor3f(*(cls.color_wave * total_level))
        glBegin(GL_LINES)
        for pair in cls.wave_vertices:
            glVertex2fv(pair)
        glEnd()


class WaterSource(Sprite):
    color = np.array((.6, .6, 1.))
    vertices = [
        (0, 0),
        (1, 0),
        (1, 1),
        (0, 1)
    ]

    @classmethod
    def configure(cls, padding=None):
        if padding is not None:
            cls.padding = padding

    @classmethod
    def draw(cls):
        glPolygonMode(GL_FRONT, GL_FILL)
        glColor3f(*cls.color)
        glBegin(GL_QUADS)
        for pair in cls.vertices:
            glVertex2fv(pair)
        glEnd()


class Renderer:
    def __init__(self):
        self.scale = 8
        self.objects = {
            "ground": Ground,
            "water": Water,
            "water_source": WaterSource,
        }

    def draw(self, t, coords, what, **kwargs):
        glPolygonMode(GL_FRONT, GL_FILL)
        glPushMatrix()
        glScale(self.scale, self.scale, 1)
        glTranslate(*coords, 0)
        self.objects[what].draw(**kwargs)
        glPopMatrix()
