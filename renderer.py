from typing import Dict, List

import tcod

from models.entity import Entity
from models.map_objects import Map


def render_all(con, entities: List[Entity], game_map: Map, fov_map: tcod.map.Map, fov_recompute: bool, screen_width: int, screen_height: int, colors: Dict[str, tcod.Color]):
    # Draw map tiles
    if fov_recompute:
        for y in range(game_map.height):
            for x in range(game_map.width):
                visible = tcod.map_is_in_fov(fov_map, x, y)
                wall = game_map.tiles[x][y].block_sight

                if visible:
                    if wall:
                        tcod.console_set_char_background(con, x, y, colors.get('light_wall'), tcod.BKGND_SET)
                    else:
                        tcod.console_set_char_background(con, x, y, colors.get('light_ground'), tcod.BKGND_SET)
                    game_map.tiles[x][y].explored = True
                elif game_map.tiles[x][y].explored:
                    if wall:
                        tcod.console_set_char_background(con, x, y, colors.get('dark_wall'), tcod.BKGND_SET)
                    else:
                        tcod.console_set_char_background(con, x, y, colors.get('dark_ground'), tcod.BKGND_SET)

    # Draw entities
    for entity in entities:
        draw_entity(con, entity, fov_map)
    tcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)

def clear_all(con, entities: List[Entity]):
    for entity in entities:
        clear_entity(con, entity)

def draw_entity(con, entity: Entity, fov_map: tcod.map.Map):
    if tcod.map_is_in_fov(fov_map, entity.x, entity.y):
        tcod.console_set_default_foreground(con, entity.color)
        tcod.console_put_char(con, entity.x, entity.y, entity.char, tcod.BKGND_NONE)


def clear_entity(con, entity: Entity):
    tcod.console_put_char(con, entity.x, entity.y, ' ', tcod.BKGND_NONE)