from typing import Any, Dict, List

import tcod


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
            results.append({'dead': self.owner})

        return results

    def attack(self, target) -> List[Dict[str, Any]]:
        damage = self.power - target.fighter.defense
        if damage > 0:
            return [
                {'message': f'{self.owner.name} attacks {target.name} for {damage} HP'},
            ] + target.fighter.take_damage(damage)
        else:
            return [{'message': f'{self.owner.name} attacks {target.name} but does no damage'}]


class BasicMonster:
    def take_turn(self, target, fov_map: tcod.map.Map, game_map, entities) -> List[Dict[str, Any]]:
        results = []
        if tcod.map_is_in_fov(fov_map, self.owner.x, self.owner.y):
            if self.owner.distance_to(target) >= 2:
                self.owner.move_astar(target, game_map, entities)
            elif target.fighter.hp > 0:
                results += self.owner.fighter.attack(target)
        return results
