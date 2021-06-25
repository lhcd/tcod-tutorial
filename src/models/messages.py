import tcod

import textwrap


class Message:
    def __init__(self, text: str, color: tcod.Color = tcod.white) -> None:
        self.text = text
        self.color = color


class MessageLog:
    def __init__(self, x: int, width: int, height: int) -> None:
        self.messages = []
        self.x = x
        self.width = width
        self.height = height

    def add_message(self, message: Message):
        new_message_lines = textwrap.wrap(message.text, self.width)
        for line in new_message_lines:
            if len(self.messages) == self.height:
                del self.messages[0]
            self.messages.append(Message(line, message.color))
