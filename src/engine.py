import os

import tcod

from death_handlers import kill_monster, kill_player
from engine_handlers import process_player_turn_results
from fov_handler import initialize_fov, recompute_fov
from models.game_state import GameState, RenderOrder
from input_handlers import handle_keys, handle_mouse
from models.components import Fighter, Inventory
from models.entity import Entity
from models.maps import Map
from models.messages import Message, MessageLog
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
        inventory=Inventory(26),
    )
    entities = [player]

    dirname = os.path.dirname(__file__)
    tcod.console_set_custom_font(
        "./assets/arial10x10.png", tcod.FONT_TYPE_GRAYSCALE | tcod.FONT_LAYOUT_TCOD,
    )
    tcod.console_init_root(
        screen_width, screen_height, "hm", False,
    )

    con = tcod.console_new(screen_width, screen_height)
    panel = tcod.console_new(screen_width, panel_height)

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30
    max_monsters_per_room = 3
    max_items_per_room = 10
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
        max_items_per_room,
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
    previous_game_state = game_state

    targeting_item = None

    while not tcod.console_is_window_closed():
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE, key, mouse)

        if fov_recompute:
            recompute_fov(
                fov_map,
                player.x,
                player.y,
                fov_radius,
                fov_light_walls,
                fov_algorithm,
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
            game_state,
        )
        fov_recompute = False

        tcod.console_flush()
        clear_all(con, entities)

        action = handle_keys(key, game_state)
        mouse_action = handle_mouse(mouse)

        move = action.get("move")
        pickup = action.get("pickup")
        show_inventory = action.get("show_inventory")
        drop_inventory = action.get("drop_inventory")
        inventory_index = action.get("inventory_index")
        exit = action.get("exit")
        fullscreen = action.get("fullscreen")

        left_click = mouse_action.get("left_click")
        right_click = mouse_action.get("right_click")

        player_turn_results = []
        if game_state == GameState.PLAYER_TURN:
            if move:
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
            elif pickup:
                for entity in entities:
                    if entity.item and entity.x == player.x and entity.y == player.y:
                        player_turn_results += player.inventory.add_item(entity)
                        break
                else:
                    message_log.add_message(
                        Message("There is nothing here to pick up", tcod.yellow)
                    )
            elif drop_inventory:
                previous_game_state = game_state
                game_state = GameState.DROP_INVENTORY

        if (
            previous_game_state == GameState.PLAYER_TURN
            and inventory_index is not None
            and inventory_index < len(player.inventory.items)
        ):
            item = player.inventory.items[inventory_index]
            if game_state == GameState.SHOW_INVENTORY:
                player_turn_results += player.inventory.use_item(
                    item, entities=entities, fov_map=fov_map
                )
            elif game_state == GameState.DROP_INVENTORY:
                player_turn_results += player.inventory.drop_item(item)

        if game_state == GameState.TARGETING:
            if left_click:
                target_x, target_y = left_click
                player_turn_results += player.inventory.use_item(
                    targeting_item,
                    entities=entities,
                    fov_map=fov_map,
                    target_x=target_x,
                    target_y=target_y,
                )
            elif right_click:
                player_turn_results.append({"targeting_cancelled": True})

        if show_inventory:
            previous_game_state = game_state
            game_state = GameState.SHOW_INVENTORY

        (
            game_state,
            previous_game_state,
            targeting_item,
        ) = process_player_turn_results(
            player_turn_results,
            message_log,
            player,
            game_state,
            previous_game_state,
            entities,
            targeting_item,
        )

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
            if game_state in (GameState.SHOW_INVENTORY, GameState.DROP_INVENTORY):
                game_state = previous_game_state
            elif game_state == GameState.TARGETING:
                player_turn_results.append({"targeting_cancelled": True})
            else:
                return True


if __name__ == "__main__":
    main()
