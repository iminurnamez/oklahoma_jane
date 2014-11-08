from math import pi, cos, sin
from itertools import cycle
from collections import defaultdict
from collections import deque
import pygame as pg
from .. import prepare
from angles import get_collision_sides
from items import FishingPole, Gun, Hand, Torch
        
class Adventurer(object):
    def __init__(self, center_point, start_state="Midair"):      
        flip = pg.transform.flip
        self.images = {
                        "Grounded": {"left": cycle([flip(prepare.GFX["adventurerwalk1"], True, False),
                                                                flip(prepare.GFX["adventurerwalk2"], True, False)]),
                                            "right": cycle([prepare.GFX["adventurerwalk1"],
                                                                  prepare.GFX["adventurerwalk2"]])},    
                        "Midair": {"left": cycle([flip(prepare.GFX["adventurerwalk2"], True, False)]),
                                       "right": cycle([prepare.GFX["adventurerwalk2"]])},
                        "Swinging": {"left": cycle([flip(prepare.GFX["adventurerswing"], True, False)]),
                                            "right": cycle([prepare.GFX["adventurerswing"]])},
                        "Hanging": {"left": cycle([flip(prepare.GFX["adventurerhang"], True, False)]),
                                            "right": cycle([prepare.GFX["adventurerhang"]])},
                        "Climbing": {"left": cycle([prepare.GFX["climb1"], prepare.GFX["climb2"]]),
                                           "right": cycle([prepare.GFX["climb1"], prepare.GFX["climb2"]])},
                        "Casting": {"left": cycle([flip(prepare.GFX["adventurerwalk1"], True, False)]),
                                          "right": cycle([prepare.GFX["adventurerwalk1"]])},
                        "Fishing": {"left": cycle([flip(prepare.GFX["adventurerwalk1"], True, False)]),
                                          "right": cycle([prepare.GFX["adventurerwalk1"]])}                                          
                                            }               
        self.direction = "right"
        self.pos = list(center_point)        
        self.rect = pg.Rect((0, 0), (64, 64))
        self.rect.center = self.pos
        self.velocity = [0, 0]
        self.max_velocity = 5
        self.accel = .2
        self.platform = None
        self.rope = None
        self.state = start_state
        self.image = next(self.images[self.state]["right"])
        self.hand_offset = [13, 2]        
        self.items = deque([Hand(), Gun(), FishingPole(), Torch()])
        self.item = self.items[0]
        self.shrooming = False
        self.inventory = defaultdict(int)
        self.inventory["Torches"] = 10 # TESTING
        self.land_sound = pg.mixer.Sound(prepare.SFX["land"])
        
    def move_map(self, offset, level):
        '''Adjust level.map_offset by offset'''
        size = level.map.get_size()
        if prepare.SCREEN_SIZE[0] // 2 < self.pos[0] < size[0] - (prepare.SCREEN_SIZE[0] // 2): 
            level.map_offset[0] += offset[0]
        if prepare.SCREEN_SIZE[1] // 2 < self.pos[1] < size[1] - (prepare.SCREEN_SIZE[1] // 2): 
            level.map_offset[1] += offset[1]
        
    def snap_to(self, pos, level):
        '''Set self.pos to pos and adjust level.map_offset'''
        self.move_map((pos[0] - self.pos[0],
                               pos[1] - self.pos[1]), level)
        self.pos = [pos[0], pos[1]]
        self.rect.center = self.pos
        
    def get_screen_pos(self, offset):
        screen_pos = [int(self.pos[0]) - offset[0],
                              int(self.pos[1]) - offset[1]]
        return screen_pos

    def get_hand_pos(self):
        if self.direction == "left":
            hand_offset = [self.hand_offset[0] * -1,
                                   self.hand_offset[1]]
        else:
            hand_offset = self.hand_offset
        return [self.pos[0] + hand_offset[0],
                    self.pos[1] + hand_offset[1]]
    
    def update_move(self, level):
        '''Move self.pos by self.velocity and adjust map offset'''
        self.pos = [self.pos[0] + self.velocity[0],
                        self.pos[1] + self.velocity[1]]
        self.move_map(self.velocity, level)
        self.rect.center = self.pos    
    
    def swing_rope(self, direction):
        self.state = "Swinging"
        hold = self.handhold 
        if direction == "left":
            if self.rope.momentum <= 0: 
                self.rope.momentum -= .04 * (hold.angle - (1.2 * pi))
            else:
                self.rope.momentum += .015
        elif direction == "right":
            if self.rope.momentum >= 0:            
                self.rope.momentum += .04 * ((1.8 * pi) - hold.angle)
            else:
                self.rope.momentum -= .015 
        if direction != self.direction:
            self.change_direction(direction)        
        
    def walk(self, direction): 
        if direction == "left": 
            self.velocity[0] -= self.accel
            
        elif direction == "right":
            self.velocity[0] += self.accel
        if direction != self.direction:
            self.change_direction(direction)
        self.velocity[0] = min(max(-self.max_velocity, self.velocity[0]),
                                         self.max_velocity)
        
    def jump(self):
        self.velocity[1] = max(min(-1.8, -abs(self.velocity[0])), -3)
        self.velocity[0] *= .65
        self.state = "Midair"
        
    def land(self, platform, level):
        self.state = "Grounded"
        self.snap_to((self.pos[0], platform.rect.top - (self.rect.height/2)), level)
        self.velocity[1] = 0
        self.platform = platform
                    
    def shimmy(self, direction, level):
        if not level.ticks % 6:
            segs = self.rope.segments
            if direction == "up":
                try:
                    self.handhold = segs[segs.index(self.handhold) - 1]
                except IndexError:
                    pass            
            elif direction == "down":        
                try:
                    self.handhold = segs[segs.index(self.handhold) + 1]
                except IndexError:
                    self.drop_rope(level) 
                    

    def drop_rope(self, level):
        self.snap_to(self.handhold.end_pos, level)      
        self.velocity[0] = cos(self.handhold.angle) * abs(self.rope.momentum * 1.5)
        self.velocity[1] = min(-2, -abs(self.rope.momentum))
        if ((self.handhold.angle > (1.5 * pi) and self.rope.momentum < 0)
                        or (self.handhold.angle < (1.5 * pi) and self.rope.momentum > 0)):
            self.velocity[0] *= -1
        self.state = "Midair"
        self.rope.cooldown += 100
        self.rope.swinger = None
    
    def mount_ladder(self, ladder, level):
        self.snap_to((ladder.rect.centerx, self.pos[1]), level)
        self.ladder = ladder
        self.state = "Climbing"
        self.velocity = [0, 0]
        
    def climb(self, direction, level):
            if direction == "up":
                self.pos[1] -= 1
                self.move_map((0, -1), level)
                if self.rect.bottom < self.ladder.rect.top:
                    self.dismount_ladder()                
            elif direction == "down":        
                self.pos[1] += 1
                self.move_map((0, 1), level)
                if self.rect.bottom >= self.ladder.rect.bottom - 5:
                    self.dismount_ladder()
                    self.velocity = [0, 0] 
    
    def dismount_ladder(self):        
        self.state = "Midair"
        self.item.ladder_sound.stop()
        self.ladder = None
        
    def get_event(self, event, level):
        e_keys = prepare.EVENT_KEYS
        controls = {e_keys["Up"]: {"Grounded": (self.jump, tuple())},                  
                         e_keys["Use Item"]: {"Grounded": (self.item.use, (self, level)),
                                                         "Midair": (self.item.use, (self, level)),
                                                         "Swinging": (self.item.use, (self, level)),
                                                         "Hanging": (self.item.use, (self, level)),
                                                         "Climbing": (self.item.use, (self, level))}}            
        if event.type == pg.KEYDOWN:
            try:
                controls[event.key][self.state][0](*controls[event.key][self.state][1])
            except KeyError:
                pass
                
            if (not self.item.in_use) and (self.state not in ("Swinging", "Hanging")):
                if event.key == e_keys["Previous Item"]:
                    self.item.holster()
                    self.items.rotate(1)
                    self.item = self.items[0]
                elif event.key == e_keys["Next Item"]:
                    self.item.holster()
                    self.items.rotate(-1)
                    self.item = self.items[0]
                    
    def change_direction(self, direction):
        if direction == "left":
            self.direction = "left"
        else:
            self.direction = "right"
        self.image = next(self.images[self.state][self.direction])
        
    def update(self, level, keys):
        e_keys = prepare.EVENT_KEYS
        controls = {e_keys["Left"]: {"Hanging": (self.swing_rope, ("left",)),
                                             "Swinging": (self.swing_rope, ("left",)),
                                             "Grounded": (self.walk, ("left",))},
                         e_keys["Right"]: {"Hanging": (self.swing_rope, ("right",)),
                                               "Swinging": (self.swing_rope, ("right",)),
                                               "Grounded": (self.walk, ("right",))},
                         e_keys["Up"]: {"Hanging": (self.shimmy, ("up", level)),
                                         "Swinging": (self.shimmy, ("up", level)),
                                         "Climbing": (self.climb, ("up", level))},
                         e_keys["Down"]: {"Hanging": (self.shimmy, ("down", level)),
                                               "Swinging": (self.shimmy, ("down", level)),
                                               "Climbing": (self.climb, ("down", level))}}
                                             
        for key in controls:
            if keys[key]:
                try:
                    controls[key][self.state][0](*controls[key][self.state][1])
                    break
                except KeyError:
                    pass

        if self.state in ("Hanging", "Swinging"):
            self.snap_to(self.handhold.end_pos, level)            
            if not any((keys[e_keys["Left"]], keys[e_keys["Right"]])):
                self.state = "Hanging"
            
                      
        elif self.state == "Midair":    
            if keys[e_keys["Left"]]:
                self.velocity[0] -= .015
                self.change_direction("left")
            if keys[e_keys["Right"]]:
                self.velocity[0] += .015
                self.change_direction("right")                
            
            self.velocity[0] *= .99
            self.velocity[1] = min(max(-self.max_velocity, self.velocity[1] + .05), self.max_velocity)
            self.update_move(level)    

            collision_rect = self.rect.inflate(-30, -10)
            collision_rect.bottom = self.rect.bottom
            for platform in [x for x in level.groups["platforms"] if x.rect.colliderect(collision_rect)]:                    
                    collision_sides = get_collision_sides(collision_rect, platform.rect)   
                    if "bottom" in collision_sides:
                        if platform.rect.left <= self.pos[0] <= platform.rect.right:
                            self.land_sound.play()
                            self.land(platform, level)
                    elif "top" in collision_sides:
                        self.move_map((0, platform.rect.bottom - self.rect.top), level) 
                        self.rect.top = platform.rect.bottom
                        self.velocity[1] = 0
                    elif "left" in collision_sides:
                        self.move_map((platform.rect.right - self.rect.left, 0), level)
                        self.rect.left = platform.rect.right
                        self.velocity[0] = 0
                    elif "right" in collision_sides:
                        self.move_map((platform.rect.left - self.rect.right, 0), level)
                        self.rect.right = platform.rect.left
                        self.velocity[0] = 0
                    else:
                        self.land_sound.play()
                        self.land(platform, level)
                    self.pos = list(self.rect.center)

        elif self.state == "Grounded":
            self.velocity[0] *= .95
            if abs(self.velocity[0]) < .1:
                self.velocity[0] = 0
            
            self.update_move(level)

            if not (self.platform.rect.left <= self.pos[0] <= self.platform.rect.right):
                self.platform = None
                self.state = "Midair"
            
       
        
        self.item.update(self, level, keys)         
        
        self.rect.center = self.pos
        if not level.ticks % 12:
            if not (self.state == "Grounded" and self.velocity[0] == 0): 
               self.image = next(self.images[self.state][self.direction])
            
        

                    
    def draw(self, surface, offset):
        self.item.handhold = self.get_hand_pos()
        screen_pos = self.get_screen_pos(offset)
        screen_rect=pg.Rect(self.image.get_rect(center=screen_pos))
        surface.blit(self.image, screen_rect)
        if self.state not in ("Climbing", "Hanging", "Swinging"):
            self.item.draw(surface, offset)