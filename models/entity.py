from typing import List, Optional

import tcod

class Entity:
    """
    Generic world object
    """
    def __init__(
        self,
        x: int=0, y: int=0,
        char: str='?',
        color=tcod.white,
        name: str='',
        blocks=False,
    ):
        self.x = x
        self.y = y

        self.char = char
        self.color = color
        self.name = name

        self.blocks = blocks

    def get_blocking_entity_at_location(
        entities: List['Entity'],
        x: int, y: int
    ) -> Optional['Entity']:
        """Class utility to fetch the blocking entity at a location, if any"""
        return next(filter(lambda e: e.blocks and e.x == x and e.y == y, entities), None)

    def move(self, dx: int, dy: int):
        self.x += dx
        self.y += dy
