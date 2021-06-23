from functools import reduce
from hashlib import new
from models.entity import Entity
from random import randint
from typing import List, Optional, Tuple


class Tile:
    """
    A location on a map. May be passable, may be see thru.
    """
    def __init__(self, blocked: bool, block_sight: Optional[bool]=None):
        self.blocked = blocked
        self.block_sight = block_sight if block_sight is not None else blocked
        self.explored = False

    def dig_out(self):
        self.blocked = False
        self.block_sight = False

class Rect:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x1 = x
        self.x2 = x + width
        self.y1 = y
        self.y2 = y + width

    def center(self) -> Tuple[int, int]:
        """Gets the coordinates of the center of this rectangle"""
        return (
            int((self.x1 + self.x2) / 2),
            int((self.y1 + self.y2) / 2)
        )

    def intersects(self, other: 'Rect') -> bool:
        return (
            self.x1 <= other.x2 and self.x2 >= other.x1 and
            self.y1 <= other.y2 and self.y2 >= other.y1
        )


class Map:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()

    def is_blocked(self, x: int, y: int) -> bool:
        return self.tiles[x][y].blocked

    def create_room(self, room: Rect):
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.tiles[x][y].dig_out()

    def create_rooms(self, rooms: List[Rect]):
        for room in rooms:
            self.create_room(room)

    def create_horizontal_tunnel(self, x1: int, x2: int, y: int):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].dig_out()

    def create_vertical_tunnel(self, y1: int, y2: int, x: int):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].dig_out()

    def initialize_tiles(self) -> List[List[Tile]]:
        tiles = [
            [
                Tile(True) for y in range(self.height)
            ]
            for x in range(self.width)
        ]
        return tiles

    def make_room_based_map(self, max_rooms: int, room_min_size: int, room_max_size: int, map_width: int, map_height: int, player: Entity):
        rooms = []

        for r in range(max_rooms):
            w = randint(room_min_size, room_max_size)
            h = randint(room_min_size, room_max_size)
            x = randint(0, map_width - w - 2)
            y = randint(0, map_height - h - 2)

            new_room = Rect(x, y, w, h)
            for room in rooms:
                if new_room.intersects(room):
                    break
            else:
                self.create_room(new_room)
                new_x, new_y = new_room.center()
                if len(rooms) == 0:
                    player.x = new_x
                    player.y = new_y
                else:
                    prev_x, prev_y = rooms[-1].center()
                    if randint(0, 1) == 1:
                        self.create_horizontal_tunnel(prev_x, new_x, prev_y)
                        self.create_vertical_tunnel(prev_y, new_y, new_x)
                    else:
                        self.create_vertical_tunnel(prev_y, new_y, prev_x)
                        self.create_horizontal_tunnel(prev_x, new_x, new_y)
                rooms.append(new_room)
