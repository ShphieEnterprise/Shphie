from typing import Union

from discord import Interaction, Message

import config as cfg


async def neko(orgmsg: Union[Interaction, Message], *args) -> None:
    channel, user = await cfg.botutil.convert_orgmsg(orgmsg)
    if channel is None or user is None:
        return

    await channel.send("にゃーん")
