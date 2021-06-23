import tcod
from tcod import color

from input_handlers import handle_keys
from models.entity import Entity
from models.map_objects import Map
from renderer import clear_all, render_all


def main():
    screen_width = 80
    screen_height = 50

    map_width = 80
    map_height = 45
    map_colors = {
        'dark_wall': tcod.Color(0, 0, 100),
        'dark_ground': tcod.Color(50, 50, 150),
    }

    player = Entity(int(screen_width / 2), int(screen_height / 2), '@')
    npc = Entity(int(screen_width / 2) - 5, int(screen_height / 2), '+', tcod.blue)
    entities = [npc, player]

    tcod.console_set_custom_font(
        'arial10x10.png',
        tcod.FONT_TYPE_GRAYSCALE | tcod.FONT_LAYOUT_TCOD,
    )
    tcod.console_init_root(
        screen_width,
        screen_height,
        'hm',
        False,
    )

    con = tcod.console_new(screen_width, screen_height)

    map = Map(map_width, map_height)

    key = tcod.Key()
    mouse = tcod.Mouse()

    while not tcod.console_is_window_closed():
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS, key, mouse)

        render_all(con, entities, map, screen_width, screen_height, map_colors)
        tcod.console_flush()
        clear_all(con, entities)

        action = handle_keys(key)
        move = action.get('move')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')

        if move and not map.is_blocked(player.x + move[0], player.y + move[1]):
            player.move(*move)

        if fullscreen:
            tcod.console_set_fullscreen(
                not tcod.console_is_fullscreen()
            )

        if exit:
            return True


if __name__ == '__main__':
    main()