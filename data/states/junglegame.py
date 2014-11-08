from __future__ import division
from math import pi, sin, cos
import pygame as pg
from .. import tools, prepare

from ..components.adventurer import Adventurer

from ..components.levels import Level1
        

            
class Game(tools._State):
    def __init__(self):
        super(Game, self).__init__()
        self.screen_rect = pg.Rect((0, 0), prepare.SCREEN_SIZE)
        self.elapsed = 0.0
        self.persist["level"] = Level1()
        self.level = self.persist["level"]
        self.player = Adventurer(self.level.player_start)
        self.level.player = self.player
        
    def startup(self, persistent):
        self.persist = persistent
        self.level = self.persist["level"]
        self.level.player = self.player
        
    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.done = True
                self.quit = True
            elif event.key == pg.K_q:
                self.done = True
                self.next = "CONTROLSSCREEN"
            elif event.key == pg.K_s:
                self.player.shrooming = not self.player.shrooming
            else:
                self.player.get_event(event, self.level)

    def update(self, surface, keys, dt):
        screen_rect = surface.get_rect()
        self.elapsed += dt
        while self.elapsed >=  1000.0 / self.fps:
            self.level.update(self.player)
            self.player.update(self.level, keys)
            self.elapsed -= 1000.0 / self.fps
        self.draw(surface)
        
    def draw(self, surface):
        self.level.draw(surface)
        
  
