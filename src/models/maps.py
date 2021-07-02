from models.messages import Message
from typing import List, Optional, Tuple
from random import randint

import tcod

from models.game_state import RenderOrder
from models.components import BasicMonster, Fighter, Item
from models.entity import Entity
from models.item_functions import cast_fireball, cast_lightning, heal


class Tile:
    """
    A location on a map. May be passable, may be see thru.
    """

    def __init__(self, blocked: bool, block_sight: Optional[bool] = None):
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
        return (int((self.x1 + self.x2) / 2), int((self.y1 + self.y2) / 2))

    def intersects(self, other: "Rect") -> bool:
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )

    def random_location(self) -> Tuple[int, int]:
        """Returns a random coordinate in the room"""
        return (randint(self.x1 + 1, self.x2 - 1), randint(self.y1 + 1, self.y2 - 1))


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
        tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]
        return tiles

    def place_items(self, room: Rect, entities: List[Entity], number_of_items: int):
        items = []
        for i in range(number_of_items):
            x, y = room.random_location()

            if not any(
                [entity for entity in entities if entity.x == x and entity.y == y]
            ):
                item_chance = randint(0, 100)
                if item_chance < 70:
                    item = Entity(
                        x,
                        y,
                        "!",
                        tcod.violet,
                        "Healing Potion",
                        render_order=RenderOrder.ITEM,
                        item=Item(use_function=heal, amount=4),
                    )
                elif item_chance < 85:
                    item = Entity(
                        x,
                        y,
                        "#",
                        tcod.red,
                        "Fireball Scroll",
                        render_order=RenderOrder.ITEM,
                        item=Item(
                            use_function=cast_fireball,
                            damage=20,
                            maximum_range=5,
                            radius=3,
                            targeting=True,
                            targeting_message=Message(
                                "Left-click a target tile for the fireball, or right-click to cancel.",
                                tcod.light_cyan,
                            ),
                        ),
                    )
                else:
                    item = Entity(
                        x,
                        y,
                        "#",
                        tcod.yellow,
                        "Lightning Scroll",
                        render_order=RenderOrder.ITEM,
                        item=Item(
                            use_function=cast_lightning, damage=20, maximum_range=5
                        ),
                    )
                items.append(item)
        return items

    def place_monsters(
        self, room: Rect, entities: List[Entity], number_of_monsters: int
    ) -> List[Entity]:
        monsters = []
        for i in range(number_of_monsters):
            x, y = room.random_location()
            if not any(
                [entity for entity in entities if entity.x == x and entity.y == y]
            ):
                if randint(0, 100) < 80:
                    monster = Entity(
                        x,
                        y,
                        "o",
                        tcod.desaturated_fuchsia,
                        "Orc",
                        blocks=True,
                        render_order=RenderOrder.ACTOR,
                        fighter=Fighter(hp=10, defense=0, power=3),
                        ai=BasicMonster(),
                    )
                else:
                    monster = Entity(
                        x,
                        y,
                        "T",
                        tcod.fuchsia,
                        "Troll",
                        blocks=True,
                        render_order=RenderOrder.ACTOR,
                        fighter=Fighter(hp=16, defense=1, power=4),
                        ai=BasicMonster(),
                    )
                monsters.append(monster)
        return monsters

    def place_entities(
        self,
        room: Rect,
        entities: List[Entity],
        max_monsters_per_room: int = 5,
        max_items_per_room: int = 5,
    ) -> List[Entity]:
        monster_count = randint(0, max_monsters_per_room)
        item_count = randint(0, max_items_per_room)
        entities += self.place_monsters(room, entities, monster_count)
        entities += self.place_items(room, entities, item_count)
        return entities

    def make_room_based_map(
        self,
        max_rooms: int,
        room_min_size: int,
        room_max_size: int,
        map_width: int,
        map_height: int,
        player: Entity,
        entities: List[Entity],
        max_monsters_per_room: int,
        max_items_per_room: int,
    ):
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

                self.place_entities(
                    new_room, entities, max_monsters_per_room, max_items_per_room
                )
                rooms.append(new_room)
