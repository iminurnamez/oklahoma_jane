import pygame as pg
import pytmx
from pytmx.pytmx import TiledTileLayer as TileLayer
from .platforms import Platform, Water, PlayerStart, Ladder, Vines, JungleBground, Sky, Dirt, Tree, BigTree, Darkness
from .ropeswing import RopeSwing
from .enemies import Snake, Bat
from .pickups import BananaTree, PapayaTree
from .harvestplants import TaroPlant, PineapplePlant
from .butterfly import Butterfly   

def load_level(tmx_file):
    platforms = []
    ropes = []
    ladders = []
    water = []
    player_starts = []
    vines = []
    dirt = []
    sky = []
    jungle = []
    darkness = []
    trees = []
    enemies = []
    fruit_trees = []
    harvest_plants = []
    butterflies = []
    
    classes = {"platform": Platform,
                    "ropeswing": RopeSwing,
                    "water": Water,
                    "player_start": PlayerStart,
                    "ladder": Ladder,
                    "vines": Vines,
                    "dirt": Dirt,
                    "sky": Sky,
                    "jungle": JungleBground,
                    "darkness": Darkness,
                    "tree": Tree,
                    "bigtree": BigTree,
                    "snake": Snake,
                    "bat": Bat,
                    "banana_tree": BananaTree,
                    "papaya_tree": PapayaTree,
                    "taro_plant": TaroPlant,
                    "pineapple_plant": PineapplePlant,
                    "butterfly": Butterfly}
    group_map = {"platform": "platforms",
                          "ropeswing": "ropes",
                          "water": "water",
                          "ladder": "ladders",
                          "player_start": "player_starts",
                          "vines": "vines",
                          "dirt": "dirt",
                          "darkness": "darkness",
                          "jungle": "jungle",
                          "sky": "sky",
                          "tree": "trees",
                          "bigtree": "trees",
                          "enemy": "enemies",
                          "banana_tree": "fruit_trees",
                          "papaya_tree": "fruit_trees",
                          "taro_plant": "harvest_plants",
                          "pineapple_plant": "harvest_plants",
                          "butterfly": "butterflies"}
    groups = {"platforms": platforms,
                    "ropes": ropes,
                    "ladders": ladders,
                    "water": water,
                    "player_starts": player_starts,
                    "vines": vines,
                    "dirt": dirt,
                    "darkness": darkness,
                    "sky": sky,
                    "jungle": jungle,
                    "trees": trees, 
                    "enemies": enemies,
                    "fruit_trees": fruit_trees,
                    "harvest_plants": harvest_plants,
                    "butterflies": butterflies}
    
    tmx = pytmx.load_pygame(tmx_file, colorkey=(0,0,0, 255))
    tile_width, tile_height = tmx.tilewidth, tmx.tileheight
    width, height = tmx.width * tile_width, tmx.height * tile_height
    surface = pg.Surface((width, height)).convert()
    surface.fill(pg.Color("black"))
    surface.set_colorkey(pg.Color("black"))    
    
    for layer in tmx.layers:
        if isinstance(layer, TileLayer):
            for x, y, gid in layer:
                tile = tmx.get_tile_image_by_gid(gid)
                if tile:
                    surface.blit(tile, (x * tile_width, y * tile_height))
                   
                    
    for obj in tmx.objects:
        rect = pg.Rect(obj.x, obj.y, obj.width, obj.height)
        if obj.name == "enemy":
            props = obj.properties
            klass = classes[props["class"]]
            direction = props["direction"]
            groups[group_map[obj.name]].append(klass(rect, direction))
        else:
            klass = classes[obj.name]
            groups[group_map[obj.name]].append(klass(rect))
    return groups, surface