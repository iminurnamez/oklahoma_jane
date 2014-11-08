import pygame as pg


class Butterfly(object):
    colors = ["blue", "red", "green", "yellow", "pink"]
    velocities = {(x, y) for x in (-1, 0, 1) for y in (-1, 0, 1)}
    
    def __init__(self, rect):
        self.color = chocie(self.colors)
        self.images = cycle([prepare.GFX["butterfly{}{}".format(self.color, 1)],
                                       prepare.GFX["butterfly{}{}".format(self.color, 2)]])
        self.image =  next(self.images)
        self.rect = self.image.get_rect(center=rect.center)
        self.pos = list(self.rect.center)
        self.fly_rect = rect
        self.done = False
        self.caught = False
        self.velocity = choice(self.velocities)
        
    def catch(self, player):
        player.inventory["{} Butterfly".format(self.color.title())] += 1       
    
    def update(self, player, level):
        if not self.caught:
            if not randint(0, 200):
                self.velocity = choice(self.velocities)
            self.pos[0] += self.velocity[0] * self.speed
            self.pos[1] += self.velcoity[1] * self.speed
            self.rect.center = self.pos
            self.rect.clamp_ip(self.fly_rect)
        if not level.ticks % 8:
            self.image = next(self.images)        
        
    def draw(self, surface, offset):
        screen_pos = self.get_screen_pos(offset)
        screen_rect = self.image.get_rect(center=screen_pos)
        surface.blit(self.image, screen_rect)
        