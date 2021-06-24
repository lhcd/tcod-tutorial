from typing import Tuple

import tcod

from game_state import GameState
from models.entity import Entity
from game_state import RenderOrder



def kill_player(player: Entity) -> Tuple[str, GameState]:
    player.char = '%'
    player.color = tcod.dark_red

    return 'You died!', GameState.PLAYER_DEAD


def kill_monster(monster: Entity) -> str:
    death_message = f'{monster.name} is dead!'
    monster.char = '%'
    monster.color = tcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = f'remains of {monster.name}'
    monster.render_order = RenderOrder.CORPSE

    return death_message