from discord import Message

import commands
from botutility import BotUtility


class Action(BotUtility):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.PATTERNS: dict[str, str] = {
            "slash_command": r"^/.*",
        }

    async def slash_command(self, message: Message) -> None:
        """ スラッシュコマンド """

        cmd, *args = message.content.split()
        if (cmd := cmd[1:]) in dir(commands):  # Command() function list
            await eval(f"commands.{cmd}(message, {args})")
