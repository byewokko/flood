import pygame as pg
import numpy as np
import typing
import yaml





class Game:
    def __init__(self, config_file):
        self.Objects = None
        self.Config = {}
        self.Screen: typing.Optional[pg.Surface] = None
        self.ScreenRect = pg.Rect(0, 0, 640, 640)
        self.Clock = pg.time.Clock()
        self.load_config(config_file)
        self.initialize_pygame()


    def load_config(self, config_file):
        with open(config_file, "r") as f:
            self.Config = yaml.load(f)

    def initialize_pygame(self):
        if pg.get_sdl_version()[0] == 2:
            pg.mixer.pre_init(44100, 32, 2, 1024)
        pg.init()
        if pg.mixer and not pg.mixer.get_init():
            print("Warning, no sound")
            pg.mixer = None

        fullscreen = False
        # Set the display mode
        winstyle = 0  # |FULLSCREEN
        bestdepth = pg.display.mode_ok(self.ScreenRect.size, winstyle, 32)
        self.Screen = pg.display.set_mode(self.ScreenRect.size, winstyle, bestdepth)
        self.Background = pg.Surface(self.ScreenRect.size)

    def run(self):
        """
        Execute the game loop
        """
        while True:
            # get input
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    return

            # update all the sprites
            self.Objects.update()
            keystate = pg.key.get_pressed()

            # clear/erase the last drawn sprites
            self.Objects.clear(self.Screen, self.Background)

            # handle player input
            direction = keystate[pg.K_RIGHT] - keystate[pg.K_LEFT]

            # draw the scene
            dirty = self.Objects.draw(self.Screen)
            pg.display.update(dirty)

            # cap the framerate at 40fps. Also called 40HZ or 40 times per second.
            self.Clock.tick(40)


def main(winstyle=0):
    # Load images, assign to sprite classes
    # (do this before the classes are used, after screen setup)
    img = load_image("player1.gif")
    Player.images = [img, pg.transform.flip(img, 1, 0)]
    img = load_image("explosion1.gif")
    Explosion.images = [img, pg.transform.flip(img, 1, 1)]
    Alien.images = [load_image(im) for im in ("alien1.gif", "alien2.gif", "alien3.gif")]
    Bomb.images = [load_image("bomb.gif")]
    Shot.images = [load_image("shot.gif")]

    # decorate the game window
    icon = pg.transform.scale(Alien.images[0], (32, 32))
    pg.display.set_icon(icon)
    pg.display.set_caption("Pygame Aliens")
    pg.mouse.set_visible(0)

    # create the background, tile the bgd image
    bgdtile = load_image("background.gif")
    background = pg.Surface(SCREENRECT.size)
    for x in range(0, SCREENRECT.width, bgdtile.get_width()):
        background.blit(bgdtile, (x, 0))
    screen.blit(background, (0, 0))
    pg.display.flip()
