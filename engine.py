import tcod
from tcod import color

from fov_handler import initialize_fov, recompute_fov
from input_handlers import handle_keys
from models.entity import Entity
from models.map_objects import Map
from renderer import clear_all, render_all


def main():
    screen_width = 80
    screen_height = 50

    map_width = 80
    map_height = 50
    map_colors = {
        'dark_wall': tcod.Color(0, 0, 100),
        'dark_ground': tcod.Color(50, 50, 150),
        'light_wall': tcod.Color(130, 110, 50),
        'light_ground': tcod.Color(200, 180, 50),
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

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30
    game_map = Map(map_width, map_height)
    game_map.make_room_based_map(max_rooms, room_min_size, room_max_size, map_width, map_height, player)

    npc.x = player.x - 3
    npc.y = player.y

    fov_algorithm = tcod.FOV_PERMISSIVE_0
    fov_light_walls = True
    fov_radius = 10
    fov_recompute = True
    fov_map = initialize_fov(game_map)

    key = tcod.Key()
    mouse = tcod.Mouse()

    while not tcod.console_is_window_closed():
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS, key, mouse)

        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, fov_radius, fov_light_walls, fov_algorithm)

        render_all(con, entities, game_map, fov_map, fov_recompute, screen_width, screen_height, map_colors)
        fov_recompute = False

        tcod.console_flush()
        clear_all(con, entities)

        action = handle_keys(key)
        move = action.get('move')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')

        if move and not game_map.is_blocked(player.x + move[0], player.y + move[1]):
            player.move(*move)
            fov_recompute = True

        if fullscreen:
            tcod.console_set_fullscreen(
                not tcod.console_is_fullscreen()
            )

        if exit:
            return True



if __name__ == '__main__':
    main()