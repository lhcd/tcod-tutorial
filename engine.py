import tcod

from death_handlers import kill_monster, kill_player
from fov_handler import initialize_fov, recompute_fov
from game_state import GameState, RenderOrder
from input_handlers import handle_keys
from models.components import Fighter
from models.entity import Entity
from models.maps import Map
from models.messages import MessageLog
from renderer import clear_all, render_all


def main():
    screen_width = 80
    screen_height = 50

    bar_width = 20
    panel_height = 7
    panel_y = screen_height - panel_height

    message_x = bar_width + 2
    message_width = screen_width - bar_width - 2
    message_height = panel_height - 1

    map_width = 80
    map_height = 45
    map_colors = {
        "dark_wall": tcod.Color(0, 0, 100),
        "dark_ground": tcod.Color(50, 50, 150),
        "light_wall": tcod.Color(130, 110, 50),
        "light_ground": tcod.Color(200, 180, 50),
    }

    player = Entity(
        0,
        0,
        "@",
        tcod.white,
        name="Player",
        blocks=True,
        render_order=RenderOrder.ACTOR,
        fighter=Fighter(hp=30, defense=2, power=5),
    )
    entities = [player]

    tcod.console_set_custom_font(
        "arial10x10.png",
        tcod.FONT_TYPE_GRAYSCALE | tcod.FONT_LAYOUT_TCOD,
    )
    tcod.console_init_root(
        screen_width,
        screen_height,
        "hm",
        False,
    )

    con = tcod.console_new(screen_width, screen_height)
    panel = tcod.console_new(screen_width, panel_height)

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
        max_monsters_per_room,
    )

    fov_algorithm = tcod.FOV_PERMISSIVE_0
    fov_light_walls = True
    fov_radius = 10
    fov_recompute = True
    fov_map = initialize_fov(game_map)

    message_log = MessageLog(message_x, message_width, message_height)

    key = tcod.Key()
    mouse = tcod.Mouse()

    game_state = GameState.PLAYER_TURN

    while not tcod.console_is_window_closed():
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE, key, mouse)

        if fov_recompute:
            recompute_fov(
                fov_map, player.x, player.y, fov_radius, fov_light_walls, fov_algorithm
            )

        render_all(
            con,
            panel,
            entities,
            player,
            game_map,
            fov_map,
            fov_recompute,
            message_log,
            screen_width,
            screen_height,
            bar_width,
            panel_height,
            panel_y,
            mouse,
            map_colors,
        )
        fov_recompute = False

        tcod.console_flush()
        clear_all(con, entities)

        action = handle_keys(key)
        move = action.get("move")
        exit = action.get("exit")
        fullscreen = action.get("fullscreen")

        player_turn_results = []
        if move and game_state == GameState.PLAYER_TURN:
            dx, dy = move
            destination_x = player.x + dx
            destination_y = player.y + dy
            if not game_map.is_blocked(destination_x, destination_y):
                target = Entity.get_blocking_entity_at_location(
                    entities, destination_x, destination_y
                )
                if target:
                    player_turn_results += player.fighter.attack(target)
                else:
                    player.move(*move)
                    fov_recompute = True

                game_state = GameState.ENEMY_TURN

        for result in player_turn_results:
            message = result.get("message")
            dead_entity = result.get("dead")

            if message:
                message_log.add_message(message)

            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                else:
                    message = kill_monster(dead_entity)

                message_log.add_message(message)

        if game_state == GameState.ENEMY_TURN:
            for entity in entities:
                if entity.ai:
                    enemy_turn_results = entity.ai.take_turn(
                        player, fov_map, game_map, entities
                    )
                    for result in enemy_turn_results:
                        message = result.get("message")
                        dead_entity = result.get("dead")

                        if message:
                            message_log.add_message(message)

                        if dead_entity:
                            if dead_entity == player:
                                message, game_state = kill_player(dead_entity)
                            else:
                                message = kill_monster(dead_entity)

                            message_log.add_message(message)

                if game_state == GameState.PLAYER_DEAD:
                    break
            else:
                game_state = GameState.PLAYER_TURN

        if fullscreen:
            tcod.console_set_fullscreen(not tcod.console_is_fullscreen())

        if exit:
            return True


if __name__ == "__main__":
    main()
