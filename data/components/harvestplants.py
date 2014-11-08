from random import randint
import pygame as pg
from .. import prepare


class HarvestPlant(object):
    pluck_sound = pg.mixer.Sound(prepare.SFX["pluck"])
    def __init__(self, rect, name, image_name):
        self.name = name
        self.image = prepare.GFX[image_name]
        self.rect = self.image.get_rect(midbottom=rect.midbottom)
        self.pos = list(self.rect.center)
        self.grown = True
        
    def update(self):
        if not self.grown:
            if not randint(0, 10000):
                self.grown = True
                
    def harvest(self, player):
        self.pluck_sound.play()
        for crop in self.crops:
            player.inventory[crop] += randint(self.crops[crop][0],
                                                              self.crops[crop][1])
        self.grown = False    

    def draw(self, surface, offset):
        if self.grown:
            surface.blit(self.image, self.rect.move((-offset[0], -offset[1])))
    
    
class TaroPlant(HarvestPlant):
    def __init__(self, rect):
        super(TaroPlant, self).__init__(rect, "Taro Plant", "taro")
        self.crops = {"Taro Root": (1, 4)}
        
        
class PineapplePlant(HarvestPlant):
    def __init__(self, rect):
        super(PineapplePlant, self).__init__(rect, "Pineapple Plant", "pineappleplant")
        self.crops = {"Pineapple": (1, 1)}
        self.pineapple_image = prepare.GFX["pineapple"]
        
    def draw(self, surface, offset):
        screen_rect = self.rect.move((-offset[0], -offset[1]))
        surface.blit(self.image, screen_rect)
        if self.grown:
            surface.blit(self.pineapple_image, (screen_rect.left + 12, screen_rect.top + 6))