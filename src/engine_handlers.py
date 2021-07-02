from typing import Dict, List, Optional, Tuple

from death_handlers import kill_monster, kill_player
from models.game_state import GameState
from models.entity import Entity
from models.messages import Message, MessageLog


def process_player_turn_results(
    player_turn_results: List[Dict[str, any]],
    message_log: MessageLog,
    player: Entity,
    game_state: GameState,
    previous_game_state: GameState,
    entities: List[Entity],
    targeting_item: Optional[Entity],
) -> Tuple[GameState, GameState, Entity]:
    for result in player_turn_results:
        message = result.get("message")
        dead_entity = result.get("dead")
        item_added = result.get("item_added")
        item_dropped = result.get("item_dropped")
        item_consumed = result.get("consumed")
        targeting = result.get("targeting")
        targeting_cancelled = result.get("targeting_cancelled")

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

        if targeting:
            previous_game_state = GameState.PLAYER_TURN
            game_state = GameState.TARGETING
            targeting_item = targeting

            message_log.add_message(targeting_item.item.targeting_message)

        if targeting_cancelled:
            game_state = previous_game_state
            message_log.add_message(Message("Targeting cancelled"))

    return game_state, previous_game_state, targeting_item
