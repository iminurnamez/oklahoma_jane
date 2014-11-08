from random import randint, choice
import pygame as pg


class ShroomFilter(object):
    def __init__(self, size):
        size = pg.display.get_surface().get_size()
        self.surface = pg.Surface(size).convert_alpha()
        #self.surface.set_alpha(50)
        self.colors = [(0, 0, 127, 127), (127, 0, 0, 127), (127, 0, 127, 127),
                            (0, 127, 0, 127), (127, 127, 127, 127)]
        self.ticks = 0
        
        
    def update(self):
       self.ticks += 1
        
    def draw(self, surface):
        if not self.ticks % 5:
            self.surface.fill(choice(self.colors))
        
        surface.blit(self.surface, (0, 0))
        