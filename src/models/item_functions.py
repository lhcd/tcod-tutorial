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
