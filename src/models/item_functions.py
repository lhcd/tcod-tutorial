from typing import Any, Dict, List

import tcod

from models.messages import Message


def heal(*args, **kwargs) -> List[Dict[str, Any]]:
    entity = args[0]
    amount = kwargs.get("amount", 0)
    results = []
    if entity.fighter.hp == entity.fighter.max_hp:
        results.append(
            {
                "consumed": False,
                "message": Message("You're already healthy!", tcod.yellow),
            }
        )
    else:
        amount_healed = entity.fighter.heal(amount)
        results.append(
            {
                "consumed": True,
                "message": Message(
                    f"Ahh, refreshing. You heal {amount_healed} HP", tcod.green
                ),
            }
        )
    return results


def cast_lightning(*args, **kwargs) -> List[Dict[str, Any]]:
    caster = args[0]
    entities = kwargs.get("entities")
    fov_map = kwargs.get("fov_map")
    damage = kwargs.get("damage")
    maximum_range = kwargs.get("maximum_range")

    results = []
    target = None
    closest_distance = maximum_range + 1
    for entity in entities:
        if (
            entity.fighter
            and entity != caster
            and tcod.map_is_in_fov(fov_map, entity.x, entity.y)
        ):
            distance = caster.distance_to(entity)
            if distance < closest_distance:
                target = entity
                closest_distance = distance

    if target:
        results.append(
            {
                "consumed": True,
                "target": target,
                "message": Message(
                    f"A lightning bolt strikes the {target.name} with a loud crack! It takes {damage}",
                    tcod.orange,
                ),
            }
        )
        results += target.fighter.take_damage(damage)
    else:
        results.append(
            {
                "consumed": False,
                "target": None,
                "message": Message("No target found.", tcod.yellow),
            }
        )
    return results


def cast_fireball(*args, **kwargs) -> List[Dict[str, Any]]:
    entities = kwargs.get("entities")
    fov_map = kwargs.get("fov_map")
    damage = kwargs.get("damage")
    radius = kwargs.get("radius")
    maximum_range = kwargs.get("maximum_range")
    target_x = kwargs.get("target_x")
    target_y = kwargs.get("target_y")

    results = []
    if not tcod.map_is_in_fov(fov_map, target_x, target_y):
        return [
            {
                "consumed": False,
                "message": Message(
                    "You cannot target a tile outside your field of view",
                    tcod.yellow,
                ),
            }
        ]
    results.append(
        {
            "consumed": True,
            "message": Message(
                f"The fireball explodes, burning everything within {maximum_range} tiles!",
                tcod.orange,
            ),
        }
    )

    for entity in entities:
        if entity.distance(target_x, target_y) < radius and entity.fighter:
            results.append(
                {
                    "message": Message(
                        f"The {entity.name} is burned for {damage} HP!", tcod.orange
                    )
                }
            )
            results += entity.fighter.take_damage(damage)
    return results
