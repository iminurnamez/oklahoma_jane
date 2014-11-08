from math import pi
from random import randint, choice
from itertools import cycle
import pygame as pg
from pygame.transform import flip, rotate
from .. import prepare
from angles import get_collision_sides, get_angle, project

           
class Enemy(object):
    def __init__(self, rect, direction, name, hit_points, start_state="Midair"):  
        self.name = name
        self.hp = hit_points
        self.state = start_state
        self.direction = direction
        self.image = next(self.images[self.state][self.direction])        
        self.rect = self.image.get_rect(midbottom=rect.midbottom)
        self.pos = list(self.rect.center)
        self.velocity = [0, 0]
        self.max_velocity = 5
        self.accel = .2
        self.platform = None
        self.rope = None
        self.dead_ticks = 0
        self.done = False
        self.ticks = 0
        
    def get_screen_pos(self, offset):
        screen_pos = [int(self.pos[0]) - offset[0],
                              int(self.pos[1]) - offset[1]]
        return screen_pos
        
    def flip_direction(self):
        if self.direction == "right":
            self.direction = "left"
        else:
            self.direction = "right"
        self.velocity[0] = 0
        self.pos = list(self.rect.center)
        self.update_image()
        
    def update_image(self):
        self.image = next(self.images[self.state][self.direction])
    
    def update_move(self, level):
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        self.rect.center = self.pos
        
    def land(self, platform):
        self.velocity[1] = 0
        self.rect.bottom = platform.rect.top
        self.pos = list(self.rect.center)
        self.platform = platform
        self.state = "Idle"
        
    def attack(self, player):
        pass   
        
    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.state = "Dead"
            self.update_image()
            
    def fall(self, level):
        self.velocity[0] *= .99
        self.velocity[1] = min(max(-5, self.velocity[1] + .05), 5)
        for platform in [x for x in level.groups["platforms"] if x.rect.colliderect(self.rect)]:
                collision_sides = get_collision_sides(self.rect, platform.rect)   
                if "bottom" in collision_sides:
                    if platform.rect.left <= self.pos[0] <= platform.rect.right:
                        self.land(platform)
                elif "top" in collision_sides:
                    self.rect.top = platform.rect.bottom
                    self.velocity[1] = 0
                elif "left" in collision_sides:
                    self.rect.left = platform.rect.right
                    self.velocity[0] = 0
                elif "right" in collision_sides:
                    self.rect.right = platform.rect.left
                    self.velocity[0] = 0
                else:
                    self.land(platform)
                self.pos = list(self.rect.center)
        
    def draw(self, surface, offset):
        screen_pos = self.get_screen_pos(offset)
        screen_rect=pg.Rect(self.image.get_rect(center=screen_pos))
        surface.blit(self.image, screen_rect)
   
        
        
class Bat(Enemy):
    def __init__(self, rect, direction):
        self.images = {"Idle": {"right": cycle([prepare.GFX["batidle"]]),
                                           "left": cycle([flip(prepare.GFX["batidle"], True, False)])},
                              "Pursuit": {"right": cycle([prepare.GFX["bat1"], 
                                                                    prepare.GFX["bat2"]]),
                                               "left": cycle([flip(prepare.GFX["bat1"], True, False),
                                                                  flip(prepare.GFX["bat2"], True, False)])},
                              "Dead": {"right": cycle([rotate(prepare.GFX["batidle"], 90)]),
                                            "left": cycle([rotate(prepare.GFX["batidle"], 90)])},
                              "Midair": {"right": cycle([rotate(prepare.GFX["bat1"], 270)]),
                                            "left": cycle([flip(rotate(prepare.GFX["bat1"], 270), True, False)])}}
        super(Bat, self).__init__(rect, direction, "Bat", 1, "Idle")
        self.speed = 1.5
        
    def land(self, platform):
        self.velocity[1] = 0
        self.rect.bottom = platform.rect.top
        self.pos = list(self.rect.center)
        self.platform = platform
        self.state = "Dead"
        self.update_image()
        self.rect = self.image.get_rect(center=self.pos)
        
    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.state = "Midair"
            self.velocity = [0, 0]
            self.update_image()
        
    def update(self, player, level):
        self.ticks += 1
        p_rect = player.rect.inflate(-30, -10)
        p_rect.bottom = player.rect.bottom
                    
        if self.state == "Midair":
            self.fall(level)
            self.pos[0] += self.velocity[0]
            self.pos[1] += self.velocity[1]
            self.rect.center = self.pos
            
            
        elif self.state == "Idle":
            if p_rect.colliderect(self.rect.inflate(600, 600)):
                self.state = "Pursuit"

        elif self.state == "Pursuit":
            angle = get_angle(self.pos, p_rect.center)
            if (.5 * pi) < angle < (1.5 * pi):
                self.direction = "left"
            else:
                self.direction = "right"
            self.pos = list(project(self.pos, angle, self.speed))
            self.rect.center = self.pos
            if not self.ticks % 6:
                self.image = next(self.images[self.state][self.direction])
            if self.rect.colliderect(p_rect):
                self.attack(player)
        
        elif self.state == "Dead":
            self.dead_ticks += 1
            if self.dead_ticks > 600:
                self.done = True

    
class Snake(Enemy):
    def __init__(self, rect, direction):
        self.images = {"Idle": {"right": cycle([prepare.GFX["snake"]]),
                                           "left": cycle([flip(prepare.GFX["snake"], True, False)])},
                              "Midair": {"right": cycle([prepare.GFX["snake"]]),
                                             "left": cycle([flip(prepare.GFX["snake"], True, False)])},
                              "Dead": {"left": cycle([flip(prepare.GFX["snake"], False, True)]),
                                            "right": cycle([flip(prepare.GFX["snake"], False, True)])}}
        super(Snake, self).__init__(rect, direction, "Snake", 2)
              
    def attack(self, player):
        pass
        
    def update(self, player, level):        
        self.ticks += 1
        p_rect = player.rect.inflate(-30, -10)
        p_rect.bottom = player.rect.bottom
        
        if self.state == "Midair":  
            self.fall(level)
            self.update_move(level)
            
        elif self.state == "Idle":
            if not (self.platform.rect.left <= self.pos[0] <= self.platform.rect.right):
                self.platform = None
                self.state = "Midair"
            else:
                if self.rect.left < self.platform.rect.left:
                    self.rect.left = self.platform.rect.left + 1 
                    self.flip_direction()
                elif self.rect.right > self.platform.rect.right:
                    self.rect.right = self.platform.rect.right - 1
                    self.flip_direction()
                
                if self.direction == "left":
                    self.velocity[0] = max(self.velocity[0] - self.accel, -2)
                elif self.direction == "right":
                    self.velocity[0] = min(self.velocity[0] + self.accel, 2)
                    
                self.update_move(level)
        
        elif self.state == "Attacking":
            if self.rect.colliderect(p_rect):
                self.attack(player)                
                
        elif self.state == "Dead":
            self.dead_ticks += 1
            if self.dead_ticks > 600:
                self.done = True
                

class Goat(Enemy):
    def __init__(self, rect, direction):
        super(Goat, self).__init__()