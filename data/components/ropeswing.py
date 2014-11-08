from math import pi, cos, sin
import pygame as pg
from ..components.angles import project

GRAVITY = .02

class RopeSegment(object):
    def __init__(self, centerx, topy, length, thickness, color):
       self.pos = [centerx, topy]
       self.length = length
       self.thickness = thickness
       self.color = color
       self.momentum = 0.0
       self.angle = 1.5 * pi
       self.end_pos = list(project(self.pos, self.angle, self.length))

       
    def draw(self, surface, offset):
        int_pos = [int(self.pos[0] - offset[0]), int(self.pos[1] - offset[1])]
        int_end = [int(self.end_pos[0] - offset[0]), int(self.end_pos[1] - offset[1])]
        pg.draw.line(surface, self.color, int_pos, int_end, self.thickness)
        
        
class RopeSwing(object):
    def __init__(self, rect, segment_length=10, 
                         thickness=2, color=(0, 40, 0)):
        self.pos = [rect.centerx, rect.top]
        self.length = rect.height
        self.segment_length = segment_length
        self.thickness = thickness
        self.color = color
        self.angle_increment = .005
        self.momentum = 0.0
        self.swinger = None
        self.cooldown = 0
        self.segments = []
        for y in range(0, self.length, self.segment_length):
            self.segments.append(RopeSegment(rect.centerx, rect.top + y,
                                                                   self.segment_length,
                                                                   self.thickness, self.color))                                                                  

    def update(self):
        self.cooldown = max(0, self.cooldown - 1)
        self.momentum *= .99 
        bottom = self.segments[-1]
        if bottom.angle < 1.5 * pi:
            self.momentum += GRAVITY
        elif bottom.angle > 1.5 * pi: 
            self.momentum -= GRAVITY
        self.momentum = min(max(-10, self.momentum), 10)
        if bottom.angle < 1.1 * pi and self.momentum < 0:
            self.momentum *= .95
        elif bottom.angle > 1.9 * pi and self.momentum > 0:
            self.momentum *= .95
        
        momentum = self.momentum    
        for seg in self.segments[::-1]:
            seg.angle = (seg.angle + (self.angle_increment * momentum))
            momentum *= .97     
        
        end_pos = self.pos
        for segment in self.segments:
            segment.pos = end_pos
            end_pos = list(project(segment.pos, segment.angle,
                                        segment.length))               
            segment.end_pos = end_pos
        
        if (-.1 < self.momentum < .1) and ((1.5 * pi) - .001 < bottom.angle < (1.5 * pi) + .001):
            self.momentum = 0
            bottom.angle = 1.5 * pi           
 
    def draw(self, surface, offset):
        for segment in self.segments:
            segment.draw(surface, offset)