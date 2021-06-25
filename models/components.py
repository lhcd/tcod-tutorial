from typing import Any, Callable, Dict, List

import tcod

from models.messages import Message, MessageLog


class Fighter:
    def __init__(self, hp: int, defense: int, power: int):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power

    def take_damage(self, amount) -> List[Dict[str, Any]]:
        results = []
        self.hp -= amount

        if self.hp < 1:
            results.append({"dead": self.owner})

        return results

    def heal(self, amount) -> int:
        old_hp = self.hp
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

        return self.hp - old_hp

    def attack(self, target) -> List[Dict[str, Any]]:
        damage = self.power - target.fighter.defense
        if damage > 0:
            return [
                {
                    "message": Message(
                        f"{self.owner.name} attacks {target.name} for {damage} HP",
                        tcod.white,
                    )
                },
            ] + target.fighter.take_damage(damage)
        else:
            return [
                {
                    "message": Message(
                        f"{self.owner.name} attacks {target.name} but does no damage",
                        tcod.white,
                    )
                }
            ]


class BasicMonster:
    def take_turn(
        self, target, fov_map: tcod.map.Map, game_map, entities
    ) -> List[Dict[str, Any]]:
        results = []
        if tcod.map_is_in_fov(fov_map, self.owner.x, self.owner.y):
            if self.owner.distance_to(target) >= 2:
                self.owner.move_astar(target, game_map, entities)
            elif target.fighter.hp > 0:
                results += self.owner.fighter.attack(target)
        return results


class Item:
    def __init__(self, use_function: Callable = lambda x: None, **kwargs) -> None:
        self.use_fn = use_function
        self.function_kwargs = kwargs

    def use(self, user: "Entity") -> List[Dict[str, Any]]:
        results = []
        if self.use_fn is None:
            results.append(
                {
                    "message": Message(
                        f"The {self.owner.name} cannot be used.", tcod.yellow
                    )
                }
            )
        else:
            results += self.use_fn(user, **self.function_kwargs)
        return results


class Inventory:
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.items = []

    def add_item(self, item: Item):
        results = []
        if len(self.items) >= self.capacity:
            results.append(
                {
                    "item_added": None,
                    "message": Message("Inventory full", tcod.yellow),
                }
            )
        else:
            self.items.append(item)
            results.append(
                {
                    "item_added": item,
                    "message": Message(f"You pick up the {item.name}", tcod.blue),
                }
            )
        return results

    def remove_item(self, item: "Entity"):
        self.items.remove(item)

    def drop_item(self, item: "Entity") -> List[Dict[str, Any]]:
        results = []
        item.x = self.owner.x
        item.y = self.owner.y
        self.remove_item(item)
        results.append(
            {
                "item_dropped": item,
                "message": Message(f"You dropped the {item.name}", tcod.yellow),
            }
        )
        return results

    def use_item(self, item: "Entity", **kwargs) -> List[Dict[str, Any]]:
        results = item.item.use(self.owner, **kwargs)
        for result in results:
            if result.get("consumed"):
                self.remove_item(item)
        return results
