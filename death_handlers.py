from typing import Tuple

import tcod

from game_state import GameState
from models.entity import Entity
from models.messages import Message
from game_state import RenderOrder


def kill_player(player: Entity) -> Tuple[Message, GameState]:
    player.char = "%"
    player.color = tcod.dark_red

    return Message("You died!", tcod.red), GameState.PLAYER_DEAD


def kill_monster(monster: Entity) -> Message:
    death_message = f"{monster.name} is dead!"
    monster.char = "%"
    monster.color = tcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = f"remains of {monster.name}"
    monster.render_order = RenderOrder.CORPSE

    return Message(death_message, tcod.orange)
