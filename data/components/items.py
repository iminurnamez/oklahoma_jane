from math import pi
from random import randint
from itertools import cycle
import pygame as pg
from .. import prepare
from ..components.angles import project, get_angle

class Item(object):
    def __init__(self, name):
        self.name = name
        self.in_use = False
        

class Hand(Item):
    def __init__(self):
        super(Hand, self).__init__("Hand")
        self.pos = [0, 0]
        self.ladder_sound = pg.mixer.Sound(prepare.SFX["ladder"])        
        
    def use(self, player, level):
        player.rect.center = player.pos
        big_rect = player.rect.inflate(1000, 1000)
        
        if player.state == "Climbing":
            self.ladder_sound.stop()
            player.dismount_ladder()
            
        elif player.state in ("Grounded", "Midair"):
            foot_rect = player.rect.inflate(-40, 0)
            foot_rect.bottom = player.rect.bottom + 5
            for ladder in level.groups["ladders"]:
                if ladder.rect.colliderect(foot_rect):
                    player.mount_ladder(ladder, level)
                    self.ladder_sound.play(-1)
                    return
            for rope in [x for x in level.groups["ropes"] if not x.cooldown
                              and (big_rect.collidepoint(x.segments[0].pos)
                                      or big_rect.collidepoint(x.segments[-1].end_pos))]:
                for segment in rope.segments[::-1]:
                    if player.rect.collidepoint(segment.end_pos):
                        player.rope = rope
                        player.rope.swinger = player
                        player.state = "Hanging"
                        player.handhold = segment
                        player.rope.momentum += player.velocity[0] * 2
                        if abs(player.rope.momentum) < .5:
                            player.rope.momentum = .5
                        player.velocity = [0, 0]
                        return
            for plant in [x for x in level.groups["harvest_plants"] if x.grown]:
                if plant.rect.colliderect(player.rect):
                    plant.harvest(player)
            
        elif player.state in ("Hanging", "Swinging"):
            player.drop_rope(level)
            
            
                
    def holster(self):
        self.in_use = False
        
    def update(self, player, level, keys):
        self.pos = player.get_hand_pos()
        
        
        
        
        
    def draw(self, surface, offset):
        pass
        
        
class Fish(object):
    def __init__(self, pos, direction):
        self.name = "Fish"
        images = {"left": prepare.GFX["fish"],
                        "right": pg.transform.flip(prepare.GFX["fish"], True, False)}
        self.image = images[direction]
        self.pos = pos
        self.rect = self.image.get_rect(center=self.pos)
        
    def catch(self, player):
        player.inventory[self.name] += 1
        self.done = True
        
class FishingPole(Item):
    def __init__(self):
        super(FishingPole, self).__init__("Fishing Pole")
        self.angle = .1 * pi
        self.pole_length = 60
        self.handhold = [0, 0]
        self.line_end = [0, 0]
        self.line_velocity = [0, 0]
        self.direction = "right"
        self.landed = False
        self.in_use = False
        self.winding_up = False
        self.casted = False
        self.fish_on = False
        self.fish = None
        self.nibble = False
        self.nibble_ticks = 0
        self.whip_sound = pg.mixer.Sound(prepare.SFX["polewhip"])
        self.cast_sound = pg.mixer.Sound(prepare.SFX["fishline"])
        self.splash_sound = pg.mixer.Sound(prepare.SFX["splash"])
        self.fish_sound = pg.mixer.Sound(prepare.SFX["fishsplash"])
        
    def use(self, player, level):
        if player.state == "Grounded":
            self.in_use = True
            self.direction = player.direction
            direct = 1 if self.direction == "right" else -1
            self.angle = (.5 * pi) - (.4 * pi * direct)
            player.velocity = [0, 0]
            player.state = "Casting"
            self.handhold = player.get_hand_pos()
            self.line_end = list(project(self.handhold, self.angle, self.pole_length))
            self.winding_up = True
        
    def holster(self):
        direct = -1 if self.direction == "left" else 1
        self.angle = (.5 * pi) - (.4 * pi * direct)
        self.line_velocity = [0, 0]
        self.casted = False
        self.winding_up = False
        self.in_use = False
        self.fish_on = False
        self.fish = None
        self.landed = False
        self.nibble = False
        self.nibble_ticks = 0
                    
    def update(self, player, level, keys):
        e_keys = prepare.EVENT_KEYS
        self.angle = self.angle % (2 * pi)
        self.direction = player.direction
        direct = -1 if self.direction == "left" else 1
        if self.in_use:
            if self.winding_up:
                if keys[e_keys["Use Item"]]:
                    self.angle += .02 * direct
                    if ((self.direction == "left" and self.angle < (.1 * pi))
                            or (self.direction == "right" and self.angle > (.9 * pi))):   
                        self.holster()
                        player.state = "Grounded"
                        return
                else:
                    self.whip_sound.play()
                    self.winding_up = False
                    
                    
            elif not self.landed:        
                if not self.casted:
                    self.angle -= .03 * direct
                    self.line_velocity[0] += .025 * direct
                    self.line_velocity[1] -= .045
                    if (((self.direction == "left") and (self.angle > .8 * pi))
                            or ((self.direction == "right") and (self.angle < .2 * pi))):                  
                        self.line_end = list(project(self.handhold, self.angle, self.pole_length))
                        self.cast_sound.play()
                        self.casted = True
                else:
                    if keys[e_keys["Use Item"]]:
                        self.holster()
                        player.state = "Grounded"
                    self.line_velocity[1]  = min(self.line_velocity[1] + .02, 2)
                    self.line_end[0] += self.line_velocity[0]
                    self.line_end[1] += self.line_velocity[1]
            elif self.fish_on:
                self.line_angle = get_angle(self.line_end, project(self.handhold, self.angle, self.pole_length))
                self.line_end = project(self.line_end, self.line_angle, 3)
                self.fish.pos = self.line_end
                if self.fish.image.get_rect(center=self.fish.pos).collidepoint(project(self.handhold, self.angle, self.pole_length)):
                    self.fish.catch(player)
                    player.state = "Grounded"
                    self.holster()
                    return
            elif self.nibble:
                self.nibble_ticks = max(0, self.nibble_ticks - 1)
                if self.nibble_ticks:
                    if keys[e_keys["Use Item"]]:                
                        self.fish_on = True
                        self.fish = Fish(self.line_end, self.direction)                    
                else:
                    self.nibble = False
            elif self.landed:
                if keys[e_keys["Use Item"]]:
                    self.holster()
                    player.state = "Grounded"
                    
                if not randint(0, 1000):
                    self.fish_sound.play()
                    self.nibble = True
                    self.nibble_ticks = 50
            
                
            
            pole_end = project(self.handhold, self.angle, self.pole_length)
            if not self.casted:
                self.line_end = pole_end
            
            if not self.fish_on and not self.landed:
                for pickup in level.groups["pickups"]:
                    if pickup.rect.inflate(16, 16).collidepoint(self.line_end):
                        self.cast_sound.stop()
                        self.fish = pickup
                        pickup.spawner.spawns.remove(pickup)
                        level.groups["pickups"].remove(pickup)
                        player.state = "Fishing"
                        self.landed = True
                        self.fish_on = True
                        self.angle = (.5 * pi) - (.4 * pi * direct)
                        return
                for butterfly in level.groups["butterflies"]:
                    if butterfly.rect.collidepoint(self.line_end):
                        self.cast_sound.stop()
                        butterfly.caught = True
                        self.fish = butterfly
                        level.groups["butterflies"].remove(butterfly)
                        player.state = "Fishing"
                        self.landed = True
                        self.fish_on = True
                        self.angle = (.5 * pi) - (.4 * pi * direct)
                        return                        
                for water in level.groups["water"]:
                    if water.rect.collidepoint(self.line_end):
                        self.cast_sound.stop()
                        self.splash_sound.play()
                        self.landed = True
                        self.angle = (.5 * pi) - (.4 * pi * direct)
                        player.state = "Fishing"
                        return
                for platform in level.groups["platforms"]:
                    if platform.rect.collidepoint(self.line_end):
                        self.cast_sound.stop()
                        player.state = "Grounded"
                        self.holster()
                        return
        
        else:
            direct = 1 if self.direction == "right" else -1
            self.angle = (.5 * pi) - (.4 * pi * direct)
            self.handhold = player.get_hand_pos()
            pole_end = project(self.handhold, self.angle, self.pole_length)
            self.line_end = [pole_end[0], pole_end[1] + 15]
            
    def draw(self, surface, offset):
        pole_end = project(self.handhold, self.angle, self.pole_length)
        handhold = [self.handhold[0] - offset[0],
                           self.handhold[1] - offset[1]]
        pole_end = [pole_end[0] - offset[0],
                           pole_end[1] - offset[1]]
        line_end = [self.line_end[0] - offset[0],
                          self.line_end[1] - offset[1]]
        pg.draw.line(surface, pg.Color("saddlebrown"), handhold, pole_end)
        pg.draw.line(surface, pg.Color("gray95"), pole_end, line_end)
        if self.fish:
            fish_rect = self.fish.image.get_rect(center=line_end)
            surface.blit(self.fish.image, fish_rect)
        
        
class Bullet(object):
    def __init__(self, pos, direction):
        self.pos = pos
        direct = 1 if direction == "right" else -1
        self.velocity = [6 * direct, 0]
        self.done = False
        self.damage = 5
        
    def get_screen_pos(self, offset):
        return [self.pos[0] - offset[0],
                    self.pos[1] - offset[1]]
                    
    def update(self, level):
        self.pos[0] += self.velocity[0]
        screen_pos = self.get_screen_pos(level.map_offset)
        if not level.screen_rect.collidepoint(screen_pos):
            self.done = True
        else:
            for enemy in level.groups["enemies"]:
                if enemy.rect.collidepoint(self.pos):
                    enemy.take_damage(self.damage)
                    self.done = True
                    break
            
    def draw(self, surface, offset):
        pg.draw.rect(surface, pg.Color("white"), (self.get_screen_pos(offset), (2,2)))
            
            
class Gun(Item):
    def __init__(self):
        super(Gun, self).__init__("Pistol")
        self.images = {"left": pg.transform.flip(prepare.GFX["gunright"], True, False),
                              "right": prepare.GFX["gunright"]}
        self.image_rect = self.images["right"].get_rect()
        self.cooldown = 0
        self.hand_offsets = {"left": (-5, 0),
                                      "right": (5, 0)}
        self.pos = [0, 0]
        self.gun_sound = pg.mixer.Sound(prepare.SFX["gun"])        
        
    def use(self, player, level):
        if not self.cooldown:
            self.gun_sound.play()
            hand_pos = player.get_hand_pos()
            self.pos = [hand_pos[0] + self.hand_offsets[self.direction][0], hand_pos[1]]
            level.bullets.append(Bullet([self.pos[0], self.pos[1] - 2], self.direction))
            self.cooldown = 30
    
    def holster(self):
        self.in_use = False
        self.cooldown = 0
        
    def update(self, player, level, keys):
        self.direction = player.direction
        self.cooldown  = max(0, self.cooldown - 1)
        hand_pos = player.get_hand_pos()
        self.pos = [hand_pos[0] + self.hand_offsets[self.direction][0], hand_pos[1]]
        
    def draw(self, surface, offset):
        screen_pos = [self.pos[0] - offset[0], self.pos[1] - offset[1]]
        self.image = self.images[self.direction]
        self.image_rect.center = screen_pos
        surface.blit(self.image, self.image_rect)
        
        
class Torch(Item):
    def __init__(self):
        super(Torch, self).__init__("Torch")
        self.length = 20
        img = prepare.GFX["torchflame"]
        w, h = 16, 16
        self.flames = [img.subsurface((w * i, 0, w, h)) for i in range(4)] 
        self.flames = cycle(self.flames)
        self.flame = next(self.flames)
        self.flame_rect = self.flame.get_rect()
        self.burn_time = 1000
        self.duration = self.burn_time
        self.light_radius = 250
        self.done = False
    
    def use(self, player, level):
        self.in_use = not self.in_use
        
    def holster(self):
        self.in_use = False
        
    def update(self, player, level, keys):
        self.direction = player.direction
        hand_pos = player.get_hand_pos()
        self.pos = hand_pos
        self.end_pos = [self.pos[0], self.pos[1] - self.length]
        if self.in_use:
            self.duration -= 1
        if self.duration <= 0:
            if player.inventory["Torches"] > 0:
                player.inventory["Torches"] -= 1
                self.duration = self.burn_time
            else:
                self.done = True        
                player.items.popleft()
                player.item = player.items[0]
        if not randint(0, 30):
            self.flame = next(self.flames)
            
    def draw(self, surface, offset):
        screen_pos = [self.pos[0] - offset[0],
                              self.pos[1] - offset[1]]
        end_pos = [screen_pos[0], screen_pos[1] - self.length]
        self.flame_rect.midbottom = end_pos
        pg.draw.line(surface, pg.Color("saddlebrown"), screen_pos, end_pos)
        surface.blit(self.flame, self.flame_rect)