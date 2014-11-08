import pygame as pg
from .. import prepare, tools
from ..components.labels import Label
from ..components.key_names import KEY_NAMES


class KeyPair(object):
    font = prepare.FONTS["Indiana"]
    
    def __init__(self, topleft, total_width, height, action_name, key_name):
        self.action_name = action_name
        self.key_name = key_name
        self.rects = [pg.Rect(topleft, (total_width // 2, height)),
                           pg.Rect((topleft[0] + (total_width // 2), topleft[1]), (total_width // 2, height))]
        self.relabel()
        
    def relabel(self):
        self.action_label = Label(self.font, 24, self.action_name, "white", {"center": self.rects[0].center})    
        self.key_label = Label(self.font, 24, self.key_name, "white", {"center": self.rects[1].center})
              
    def draw(self, surface):
        for rect in self.rects:
            pg.draw.rect(surface, pg.Color("saddlebrown"), rect, 3)
        self.action_label.draw(surface)
        self.key_label.draw(surface)
        
        
class ControlsScreen(tools._State):
    def __init__(self):
        super(ControlsScreen, self).__init__()
        self.next = "GAME"
        self.screen_rect = pg.display.get_surface().get_rect()
        font = prepare.FONTS["Indiana Italic"]
        self.title = Label(font, 48, "Controls", "white", {"midtop": (self.screen_rect.centerx, 5)})
        self.select_label = Label(font, 24, "Use Up/Down Arrows to navigate. Press Enter to select.",
                                            "darkgreen", {"midtop": (self.screen_rect.centerx, self.title.rect.bottom + 10)})
        self.assign_label = Label(font, 24, "Press the key you want to assign for this action.",
                                            "darkgreen", {"midtop": (self.screen_rect.centerx, self.title.rect.bottom + 10)})
        self.exit_rect = pg.Rect(0, 0, 300, 100)
        self.exit_rect.midbottom = (self.screen_rect.centerx, self.screen_rect.bottom - 10)
        self.exit_label = Label(font, 32, "EXIT", "white", {"center": self.exit_rect.center})
                                                                                              
    def startup(self, persistent):
        self.persist = persistent
        screen = self.screen_rect
        self.key_pairs = []
        width = 300
        height = 100
        top = self.select_label.rect.bottom + 20
        for action, key in prepare.EVENT_KEYS.items():
            if key in KEY_NAMES:
                key = KEY_NAMES[key]
            self.key_pairs.append(KeyPair((screen.centerx - width, top), width * 2, height, action, key))
            top += height
        self.current_index = 0    
        self.current = self.key_pairs[self.current_index]
        self.state = "Selection"
        
    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if self.state == "Selection":
                if event.key == pg.K_DOWN:
                    self.current_index += 1
                    if self.current_index == len(self.key_pairs):
                        self.current = "Exit"                    
                    elif self.current_index == len(self.key_pairs) + 1:
                        self.current_index = 0
                        self.current = self.key_pairs[self.current_index]
                    else:
                        self.current = self.key_pairs[self.current_index]
                elif event.key == pg.K_UP:
                    self.current_index -= 1
                    if self.current_index == -1:
                        self.current = "Exit"                    
                    elif self.current_index == -2:
                        self.current_index = len(self.key_pairs) - 1
                        self.current = self.key_pairs[self.current_index]
                    else:
                        self.current = self.key_pairs[self.current_index]
                elif event.key == pg.K_RETURN:
                    if self.current == "Exit":
                        self.done = True
                    else:
                        self.state = "Assignment"
                        self.current.key_name = ""
                        self.current.relabel()
                        
            elif self.state == "Assignment":
                if event.type == pg.KEYDOWN:
                    if event.key in KEY_NAMES:
                        prepare.EVENT_KEYS[self.current.action_name] = event.key       
                        self.current.key_name = KEY_NAMES[event.key]
                        self.current.relabel()
                        self.state = "Selection"                    
    
    def update(self, surface, keys, dt):
        self.draw(surface)               
                    
    def draw(self, surface):
        surface.fill(pg.Color("black"))
        self.title.draw(surface)
        if self.state == "Selection":
            self.select_label.draw(surface)
        else:
            self.assign_label.draw(surface)
        for key_pair in self.key_pairs:
            key_pair.draw(surface)
        
        pg.draw.rect(surface, pg.Color("saddlebrown"), self.exit_rect, 3)
        if self.current == "Exit":
            pg.draw.rect(surface, pg.Color("darkgreen"), self.exit_rect, 3)
        else:
            pg.draw.rect(surface, pg.Color("darkgreen"), self.current.rects[1], 3)
        self.exit_label.draw(surface)