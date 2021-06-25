from typing import Dict, List

import tcod

from models.game_state import GameState
from models.entity import Entity
from menus import inventory_menu
from models.maps import Map
from models.messages import MessageLog


def render_all(
    con: tcod.Console,
    panel: tcod.Console,
    entities: List[Entity],
    player: Entity,
    game_map: Map,
    fov_map: tcod.map.Map,
    fov_recompute: bool,
    message_log: MessageLog,
    screen_width: int,
    screen_height: int,
    bar_width: int,
    panel_height: int,
    panel_y: int,
    mouse: tcod.Mouse,
    colors: Dict[str, tcod.Color],
    game_state: GameState,
):
    # Draw map tiles
    if fov_recompute:
        for y in range(game_map.height):
            for x in range(game_map.width):
                visible = tcod.map_is_in_fov(fov_map, x, y)
                wall = game_map.tiles[x][y].block_sight

                if visible:
                    if wall:
                        tcod.console_set_char_background(
                            con, x, y, colors.get("light_wall"), tcod.BKGND_SET
                        )
                    else:
                        tcod.console_set_char_background(
                            con, x, y, colors.get("light_ground"), tcod.BKGND_SET
                        )
                    game_map.tiles[x][y].explored = True
                elif game_map.tiles[x][y].explored:
                    if wall:
                        tcod.console_set_char_background(
                            con, x, y, colors.get("dark_wall"), tcod.BKGND_SET
                        )
                    else:
                        tcod.console_set_char_background(
                            con, x, y, colors.get("dark_ground"), tcod.BKGND_SET
                        )

    entities.sort(key=lambda x: x.render_order.value)

    # Draw entities
    for entity in entities:
        draw_entity(con, entity, fov_map)

    tcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)

    # Draw player state
    tcod.console_set_default_background(panel, tcod.black)
    tcod.console_clear(panel)
    y = 1
    for message in message_log.messages:
        tcod.console_set_default_foreground(panel, message.color)
        tcod.console_print_ex(
            panel, message_log.x, y, tcod.BKGND_NONE, tcod.LEFT, message.text
        )
        y += 1

    render_bar(
        panel,
        1,
        1,
        bar_width,
        "HP",
        player.fighter.hp,
        player.fighter.max_hp,
        tcod.light_red,
        tcod.dark_red,
        height=3,
    )

    tcod.console_set_default_foreground(panel, tcod.light_gray)
    tcod.console_print_ex(
        panel,
        1,
        0,
        tcod.BKGND_NONE,
        tcod.LEFT,
        get_names_under_mouse(mouse, entities, fov_map),
    )

    tcod.console_blit(panel, 0, 0, screen_width, panel_height, 0, 0, panel_y)

    if game_state in (GameState.SHOW_INVENTORY, GameState.DROP_INVENTORY):
        inventory_menu(
            con,
            "Press the key next to an item to use it, or esc to exit."
            if game_state == GameState.SHOW_INVENTORY
            else "Press the key next to an item to drop it, or esc to exit.",
            player.inventory,
            50,
            screen_width,
            screen_height,
        )


def clear_all(con: tcod.Console, entities: List[Entity]):
    for entity in entities:
        clear_entity(con, entity)


def draw_entity(con: tcod.Console, entity: Entity, fov_map: tcod.map.Map):
    if tcod.map_is_in_fov(fov_map, entity.x, entity.y):
        tcod.console_set_default_foreground(con, entity.color)
        tcod.console_put_char(con, entity.x, entity.y, entity.char, tcod.BKGND_NONE)


def clear_entity(con, entity: Entity):
    tcod.console_put_char(con, entity.x, entity.y, " ", tcod.BKGND_NONE)


def get_names_under_mouse(
    mouse: tcod.Mouse, entities: List[Entity], fov_map: tcod.map.Map
) -> str:
    (x, y) = (mouse.cx, mouse.cy)
    # It seems like this way of getting mouse position is broken in current tcod (?)
    # TODO: switch from deprecated `tcod.sys_check_for_event` to `tcod.event.get`
    selected_entities = list(
        filter(
            lambda e: int(e.x / 2) == x
            and int(e.y / 2) == y
            and tcod.map_is_in_fov(fov_map, e.x, e.y),
            entities,
        )
    )
    return ", ".join([e.name for e in selected_entities])


def render_bar(
    panel: tcod.Console,
    x: int,
    y: int,
    total_width: int,
    name: str,
    value: int,
    maximum: int,
    bar_color: tcod.Color,
    back_color: tcod.Color,
    height: int = 1,
):
    bar_width = int(float(value) / maximum * total_width)

    tcod.console_set_default_background(panel, back_color)
    tcod.console_rect(panel, x, y, total_width, height, False, tcod.BKGND_SCREEN)
    tcod.console_set_default_background(panel, bar_color)

    if bar_width > 0:
        tcod.console_rect(panel, x, y, bar_width, height, False, tcod.BKGND_SCREEN)

    tcod.console_set_default_foreground(panel, tcod.white)
    tcod.console_print_ex(
        panel,
        int(x + total_width / 2),
        int(y + height / 2),
        tcod.BKGND_NONE,
        tcod.CENTER,
        f"{name}: {value}/{maximum}",
    )
