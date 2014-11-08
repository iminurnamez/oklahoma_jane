from random import randint, choice
from .. import prepare
import pygame as pg


class PickupItem(object):
    def __init__(self, rect, name, image_name, spawner=None):
        self.name = name
        self.image = prepare.GFX[image_name]
        self.rect = self.image.get_rect(midbottom=rect.midbottom)
        self.spawner = spawner
    
    def draw(self, surface, offset):
        screen_pos = self.rect.x - offset[0], self.rect.y - offset[1]
        surface.blit(self.image, screen_pos)

    def catch(self, player):
        player.inventory[self.name] += 1
        
class Banana(PickupItem):
    def __init__(self, rect, spawner=None):
        super(Banana, self).__init__(rect, "Banana", "banana", spawner)
        
class Papaya(PickupItem):
    def __init__(self, rect, spawner=None):
        super(Papaya, self).__init__(rect, "Papaya", "papaya", spawner)
        

class FruitTree(object):
    def __init__(self, rect, name, image_name, fruit, max_fruit, fruit_spots):
        self.name = name
        self.image = prepare.GFX[image_name]
        self.rect = self.image.get_rect(midbottom=rect.midbottom)
        self.fruit = fruit
        self.spawns = []
        self.max_fruit = max_fruit
        self.fruit_spots = [pg.Rect(left + self.rect.left, top + self.rect.top, 10, 10) for left, top in fruit_spots]
        
    def update(self, level):
        if len(self.spawns) < self.max_fruit:
            if not randint(0, 100):
                fruit = self.fruit(choice(self.fruit_spots), self)
                self.spawns.append(fruit)
                level.groups["pickups"].append(fruit)
                
    def draw(self, surface, offset):
        screen_pos = self.rect.x - offset[0], self.rect.y - offset[1]
        surface.blit(self.image, screen_pos)
        
        
class BananaTree(FruitTree):
    def __init__(self, rect):
        super(BananaTree, self).__init__(rect, "Banana Tree", "bananatree", Banana, 2, [(95, 161), (102, 131)])
        
class PapayaTree(FruitTree):
    def __init__(self, rect):
        super(PapayaTree, self).__init__(rect, "Papaya Tree", "papayatree", Papaya, 5, 
                                                          [(70, 107), (72, 119), (85, 103), (85, 113), (71, 123), (81, 130)])
                                                                                                                                     