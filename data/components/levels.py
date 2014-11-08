import pygame as pg
from .. import prepare
from ..components.ropeswing import RopeSwing
from ..components.platforms import Platform
from ..components import level_loader
from ..components.shroomfilter import ShroomFilter
from ..components.angles import get_angle, project


        
        

class Level(object):
    def __init__(self, tmx_filename):
        self.screen_rect = pg.display.get_surface().get_rect()
        self.groups, self.map = level_loader.load_level(prepare.TMX[tmx_filename])
        self.player_start = self.groups["player_starts"][0].rect.center
        self.map_offset = [0, 0]
        startx, starty = self.player_start
        w, h = self.map.get_size()
        centerx, centery = self.screen_rect.center
        if centerx < startx < (w - centerx):
            self.map_offset[0] -= (centerx - startx)
        if centery < starty < (h - centery):
            self.map_offset[1] -= (centery - starty)
        self.groups["pickups"] = []
        self.bullets = []
        self.ticks = 0
        self.shroom_filter = ShroomFilter(self.screen_rect.size)
        self.scaler = [0, 0]
        self.scaling = "up wide"
        
    def update(self, player):
        self.ticks += 1
        for rope in self.groups["ropes"]:
            rope.update()
        for bullet in self.bullets:
            bullet.update(self)
        self.bullets = [x for x in self.bullets if not x.done]
        for tree in self.groups["fruit_trees"]:
            tree.update(self)
        for enemy in self.groups["enemies"]:
            enemy.update(player, self)
        for plant in self.groups["harvest_plants"]:
            plant.update()
        self.groups["enemies"] = [x for x in self.groups["enemies"] if not x.done]
          
    def scale_draw(self, surface):
        self.shroom_filter.update()
        temp = pg.Surface(self.screen_rect.size).convert()
        self.draw_map(temp)
        if self.scaling == "up wide":
            self.scaler[0] += 10
            if self.scaler[0] > 400:
                self.scaling = "down wide"
        elif self.scaling == "down wide":
            self.scaler[0] -= 10
            if self.scaler[0] < 20:
                self.scaling = "up high"
        elif self.scaling == "up high":
            self.scaler[1] += 10
            if self.scaler[1] > 400:
                self.scaling = "down high"
        else:
            self.scaler[1] -= 10
            if self.scaler[1] < 20:
                self.scaling = "up wide"
        surface.blit(pg.transform.scale(temp, (self.screen_rect.width + self.scaler[0],
                          self.screen_rect.height + self.scaler[1])), (0, 0))
        self.shroom_filter.draw(surface)
        
    def draw_map(self, surface):
        surface.fill(pg.Color("black"))
        for sky in self.groups["sky"]:
            sky.draw(surface, self.map_offset)
        for jungle in self.groups["jungle"]:
            jungle.draw(surface, self.map_offset)
        for dirt in self.groups["dirt"]:
            dirt.draw(surface, self.map_offset)
        surface.blit(self.map, (0, 0), pg.Rect(self.map_offset, surface.get_size()))
        screen_rect = pg.display.get_surface().get_rect(topleft=self.map_offset).inflate(200, 200)
        for tree in self.groups["trees"]:
            tree.draw(surface, self.map_offset)
        for fruit_tree in self.groups["fruit_trees"]:
            fruit_tree.draw(surface, self.map_offset)
        for rope in  [x for x in self.groups["ropes"]
                           if (screen_rect.collidepoint(x.segments[0].pos)
                               or screen_rect.collidepoint(x.segments[-1].end_pos))]:
            rope.draw(surface, self.map_offset)
        for tree in self.groups["trees"]:
            tree.draw_top(surface, self.map_offset)
        for pickup in self.groups["pickups"]:
            pickup.draw(surface, self.map_offset)
        for enemy in self.groups["enemies"]:
            enemy.draw(surface, self.map_offset)
        for bullet in self.bullets:
            bullet.draw(surface, self.map_offset)
        self.player.draw(surface, self.map_offset)
        for plant in self.groups["harvest_plants"]:
            plant.draw(surface, self.map_offset)
        for vine in self.groups["vines"]:
            vine.draw(surface, self.map_offset)
            
        #for dark in self.groups["darkness"]:
        #    dark.draw(surface, self.map_offset, self.player)
            
    def draw(self, surface):
        if self.player.shrooming:
            self.scale_draw(surface)
        else:
            self.draw_map(surface)
            
            
class Level1(Level):
    def __init__(self):
        super(Level1, self).__init__("level2")