from discord import Interaction

import commands as cmd
import config as cfg


@cfg.myclient.tree.command()
async def neko(ctx: Interaction) -> None:
    """すべてはここから始まった"""

    await cmd.neko(ctx)
