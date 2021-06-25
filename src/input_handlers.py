import tcod

from models.game_state import GameState


def handle_keys(key: tcod.Key, game_state: GameState):
    if game_state == GameState.PLAYER_TURN:
        return handle_player_turn_keys(key)
    elif game_state in (GameState.SHOW_INVENTORY, GameState.DROP_INVENTORY):
        return handle_inventory_keys(key)
    return handle_universal_player_keys(key)


def handle_player_turn_keys(key: tcod.Key):
    key_char = chr(key.c)
    if key.vk == tcod.KEY_UP or key_char == "k":
        return {"move": (0, -1)}
    elif key.vk == tcod.KEY_DOWN or key_char == "j":
        return {"move": (0, 1)}
    elif key.vk == tcod.KEY_LEFT or key_char == "h":
        return {"move": (-1, 0)}
    elif key.vk == tcod.KEY_RIGHT or key_char == "l":
        return {"move": (1, 0)}
    elif key_char == "y":
        return {"move": (-1, -1)}
    elif key_char == "u":
        return {"move": (1, -1)}
    elif key_char == "b":
        return {"move": (-1, 1)}
    elif key_char == "n":
        return {"move": (1, 1)}

    if key_char == "g":
        return {"pickup": True}
    elif key_char == "d":
        return {"drop_inventory": True}

    return handle_universal_player_keys(key)


def handle_universal_player_keys(key: tcod.Key):
    key_char = chr(key.c)
    if key_char == "i":
        return {"show_inventory": True}

    if key.vk == tcod.KEY_ENTER and key.lalt:
        return {"fullscreen": True}
    elif key.vk == tcod.KEY_ESCAPE:
        return {"exit": True}

    return {}


def handle_inventory_keys(key: tcod.Key):
    index = key.c - ord("a")
    if index >= 0:
        return {"inventory_index": index}
    return handle_universal_player_keys(key)
