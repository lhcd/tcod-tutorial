import tcod

class Entity:
    """
    Generic world object
    """
    def __init__(self, x: int=0, y: int=0, char: str='?', color=tcod.white):
        self.x = x
        self.y = y
        self.char = char
        self.color = color

    def move(self, dx: int, dy: int):
        self.x += dx
        self.y += dy