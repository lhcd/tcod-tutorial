import tcod
from tcod import color

from fov_handler import initialize_fov, recompute_fov
from game_state import GameStates
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

    player = Entity(0, 0, '@', tcod.white, blocks=True)
    entities = [player]

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
    max_monsters_per_room = 3
    game_map = Map(map_width, map_height)
    game_map.make_room_based_map(
        max_rooms,
        room_min_size,
        room_max_size,
        map_width,
        map_height,
        player,
        entities,
        max_monsters_per_room
    )

    fov_algorithm = tcod.FOV_PERMISSIVE_0
    fov_light_walls = True
    fov_radius = 10
    fov_recompute = True
    fov_map = initialize_fov(game_map)

    key = tcod.Key()
    mouse = tcod.Mouse()

    game_state = GameStates.PLAYER_TURN

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

        if move and game_state == GameStates.PLAYER_TURN:
            dx, dy = move
            destination_x = player.x + dx
            destination_y = player.y + dy
            if not game_map.is_blocked(destination_x, destination_y):
                target = Entity.get_blocking_entity_at_location(entities, destination_x, destination_y)
                if target:
                    print(f'You kick the {target.name} in the shins, much to its annoyance!')
                else:
                    player.move(*move)
                    fov_recompute = True

                game_state = GameStates.ENEMY_TURN

        if GameStates.ENEMY_TURN:
            for entity in entities:
                if entity != player:
                    print(f'The {entity.name} vibes')
            game_state = GameStates.PLAYER_TURN

        if fullscreen:
            tcod.console_set_fullscreen(
                not tcod.console_is_fullscreen()
            )

        if exit:
            return True



if __name__ == '__main__':
    main()