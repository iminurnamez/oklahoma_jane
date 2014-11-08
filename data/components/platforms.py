import pygame as pg
from .. import prepare

class Platform(object):
    
    
    def __init__(self, rect):
        self.rect = rect
        
class PlayerStart(object):
    def __init__(self, rect):
        self.rect = rect    
        
class Water(object):
    def __init__(self, rect):
        self.rect = rect
        

class Ladder(object):
    def __init__(self, rect):
        self.rect = rect
        
class Tree(object):
    def __init__(self, rect):
        self.rect = rect
        self.image = prepare.GFX["tree"]
        self.top_image = prepare.GFX["treetop"]
        
    def draw(self, surface, offset):
        screen_pos = self.rect.x - offset[0], self.rect.y - offset[1]
        surface.blit(self.image, screen_pos)
        
    def draw_top(self, surface, offset):
        screen_pos = self.rect.x - offset[0], self.rect.y - offset[1]
        surface.blit(self.top_image, screen_pos)
        
        
class BigTree(object):
    def __init__(self, rect):
        self.image = prepare.GFX["bigtree"]
        self.rect = self.image.get_rect(bottomleft=rect.bottomleft)
        
        self.top_image = prepare.GFX["treetop"]
        
    def draw(self, surface, offset):
        screen_pos = self.rect.x - offset[0], self.rect.y - offset[1]
        surface.blit(self.image, screen_pos)

    def draw_top(self, surface, offset):
        pass
        
        
class Vines(object):
    def __init__(self, rect):
        self.rect = rect
        self.image = prepare.GFX["vines"]
    
    def draw(self, surface, offset):
        screen_pos = self.rect.x - offset[0], self.rect.y - offset[1]
        surface.blit(self.image, screen_pos)
        
class Sky(object):
    def __init__(self, rect):
        self.rect = rect
        
    def draw(self, surface, offset):
        screen_pos = self.rect.x - offset[0], self.rect.y - offset[1]
        screen_rect = pg.Rect(screen_pos, self.rect.size)
        if screen_rect.colliderect(pg.display.get_surface().get_rect()):
            r, g, b = 0, 127, 127
            
            for y in range(0, screen_rect.height, 8):
                pg.draw.rect(surface, (r, g, b, 255), 
                                   (screen_rect.left, (screen_rect.bottom - 8) - y,
                                    screen_rect.width, 8))
                b = max(60, b + .5)
                #g = max(60, g - .5)
                                                                                 
            
class JungleBground(object):
    def __init__(self, rect):
        self.rect = rect
        
    def draw(self, surface, offset):
        screen_pos = self.rect.x - offset[0], self.rect.y - offset[1]
        screen_rect = pg.Rect(screen_pos, self.rect.size)
        if screen_rect.colliderect(pg.display.get_surface().get_rect()):
            r, g, b = 0, 20, 0
            
            for y in range(0, screen_rect.height, 16):
                pg.draw.rect(surface, (r, g, int(b), 255), 
                                   (screen_rect.left, (screen_rect.bottom - 16) - y,
                                    screen_rect.width, 16))
                b = min(60, b + 1)
                g = min(100, g + 2)

                
class Dirt(object):
    def __init__(self, rect):
        self.rect = rect
        
    def draw(self, surface, offset):
        screen_pos = self.rect.x - offset[0], self.rect.y - offset[1]
        screen_rect = pg.Rect(screen_pos, self.rect.size)
        if screen_rect.colliderect(pg.display.get_surface().get_rect()):
            r, g, b = 38, 23, 5
            
            for y in range(0, screen_rect.height, 32):
                pg.draw.rect(surface, (r, g, b, 255), 
                                   (screen_rect.left, screen_rect.top + y,
                                    screen_rect.width, 32))
                r = max(4, r - 1)
                g = max(2, g - 1)
            
       
class Darkness(object):
    def __init__(self, rect):
        self.rect = rect
        self.surf = pg.Surface(self.rect.size).convert_alpha()
        a = 20
        for y in range(0, self.rect.height + 1, 16):
            pg.draw.rect(self.surf, (0, 0, 0, a), (0, y, self.rect.width, 16))
            a = min(250, a + 10)
        #self.surf.set_colorkey((0,0,0,255))
        self.cover = None
        
    def draw(self, surface, offset, player):
        screen_pos = [self.rect.x - offset[0], self.rect.y - offset[1]]
        screen_rect = pg.Rect(screen_pos, self.rect.size)
        if screen_rect.colliderect(pg.display.get_surface().get_rect()):
            
            if player.item.name == "Torch" and player.item.in_use:
                pass                
            else:
                surface.blit(self.surf, screen_rect)
                