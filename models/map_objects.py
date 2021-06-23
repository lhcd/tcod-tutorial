from typing import List, Optional

class Tile:
    """
    A location on a map. May be passable, may be see thru.
    """
    def __init__(self, blocked: bool, block_sight: Optional[bool]=None):
        self.blocked = blocked
        self.block_sight = block_sight if block_sight is not None else blocked

class Map:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()

    def is_blocked(self, x: int, y: int) -> bool:
        return self.tiles[x][y].blocked

    def initialize_tiles(self) -> List[List[Tile]]:
        tiles = [
            [
                Tile(False) for y in range(self.height)
            ]
            for x in range(self.width)
        ]

        tiles[30][22].blocked = True
        tiles[30][22].block_sight = True
        tiles[31][22].blocked = True
        tiles[31][22].block_sight = True
        tiles[32][22].blocked = True
        tiles[32][22].block_sight = True

        return tiles