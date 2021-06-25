from typing import List

import tcod

from models.components import Inventory


MAX_MENU_OPTIONS = 26


def menu(
    con: tcod.Console,
    header: str,
    options: List[str],
    width: int,
    screen_width: int,
    screen_height: int,
):
    if len(options) > MAX_MENU_OPTIONS:
        raise ValueError(f"Can't have more than {MAX_MENU_OPTIONS} menu options")

    header_height = tcod.console_get_height_rect(
        con, 0, 0, width, screen_height, header
    )
    height = len(options) + header_height

    window = tcod.console_new(width, height)

    tcod.console_set_default_foreground(window, tcod.white)
    tcod.console_print_rect_ex(
        window, 0, 0, width, height, tcod.BKGND_NONE, tcod.LEFT, header
    )

    y = header_height
    letter_index = ord("a")
    for option_name in options:
        text = f"({chr(letter_index)}): {option_name}"
        tcod.console_print_ex(window, 0, y, tcod.BKGND_NONE, tcod.LEFT, text)
        y += 1
        letter_index += 1

    x = int(screen_width / 2 - width / 2)
    y = int(screen_height / 2 - height / 2)
    tcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)


def inventory_menu(
    con: tcod.Console,
    header: str,
    inventory: Inventory,
    inventory_width: int,
    screen_width: int,
    screen_height: int,
):
    if len(inventory.items) == 0:
        options = ["Inventory is empty :("]
    else:
        options = [item.name for item in inventory.items]
    menu(con, header, options, inventory_width, screen_width, screen_height)
