from typing import Dict, List

from death_handlers import kill_monster, kill_player
from models.game_state import GameState
from models.entity import Entity
from models.messages import MessageLog


def process_player_turn_results(
    player_turn_results: List[Dict[str, any]],
    message_log: MessageLog,
    player: Entity,
    game_state: GameState,
    entities: List[Entity],
) -> GameState:
    for result in player_turn_results:
        message = result.get("message")
        dead_entity = result.get("dead")
        item_added = result.get("item_added")
        item_dropped = result.get("item_dropped")
        item_consumed = result.get("consumed")

        if message:
            message_log.add_message(message)

        if dead_entity:
            if dead_entity == player:
                message, game_state = kill_player(dead_entity)
            else:
                message = kill_monster(dead_entity)
            message_log.add_message(message)

        if item_added:
            entities.remove(item_added)
            game_state = GameState.ENEMY_TURN

        if item_consumed:
            game_state = GameState.ENEMY_TURN

        if item_dropped:
            entities.append(item_dropped)
            game_state = GameState.ENEMY_TURN

    return game_state
