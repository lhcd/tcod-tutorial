from enum import Enum


class GameState(Enum):
    PLAYER_TURN = 1
    ENEMY_TURN = 2
    PLAYER_DEAD = 3


class RenderOrder(Enum):
    CORPSE = 0
    ITEM = 1
    ACTOR = 2
