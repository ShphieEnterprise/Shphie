import re
from typing import Optional

import openai
from discord import Client, Intents, Message, Object, TextChannel, Thread, utils
from discord.app_commands import CommandTree

from action import Action
from botutility import BotUtility


class MyClient(BotUtility, Client):
    def __init__(self):
        super().__init__(intents=Intents.all())

        self.GUILD: Object = Object(self.get_environvar("GUILDID"))

        self.tree = CommandTree(self)
        self.action: Action = Action()

        openai.api_key = self.get_environvar("KEY_OPENAI")

    async def setup_hook(self) -> None:
        " CommandTreeの初期化 "

        self.tree.clear_commands(guild=self.GUILD)
        self.tree.copy_global_to(guild=self.GUILD)

        await self.tree.sync(guild=self.GUILD)

    async def on_ready(self):
        """ bot起動時の処理 """

        channel: Optional[TextChannel] = utils.find(lambda c: c.name == "開発室", self.guilds[0].text_channels)

        # Post
        reply: str = "起動しました"
        await channel.send(reply)

    async def chatgpt(self, message: Message):
        """ ChatGPTによる返答 """
        escape_content: str = re.sub(r"<@(everyone|here|[!&]?[0-9]{17,20})> ", "", message.content)

        if type(message.channel) is Thread:
            thread: Thread = message.channel

            # chatgpt用にbotが作成したthreadでなければreturn
            if thread.owner != self.user:
                return

            messages: list[dict[str, str]] = []
            async for mes in thread.history():
                role: str = "assistant" if mes.author == self.user else "user"

                messages.append({"role": role, "content": mes.content})

            messages = messages[:200][::-1]

        else:
            thread: Thread = await message.create_thread(name=escape_content[:20])

            messages: list[dict[str, str]] = [{"role": "user", "content": escape_content}]

        response = openai.ChatCompletion.create(model="gpt-3.5", messages=messages)

        reply = "\n".join([choice["message"]["content"] for choice in response["choices"]])
        await thread.send(reply)

    async def check_trigger(self, message: Message):
        """ messageをチェックしてアクションを実行する """

        for (trigger, pattern) in self.action.PATTERNS.items():
            if re.findall(pattern, message.content):
                await eval(f"self.action.{trigger}(message)")

    async def on_message(self, message: Message):
        """ メッセージを受け取った時の処理 """

        if self.user in message.mentions or type(message.channel) is Thread:
            # 自身のメッセージは無視
            if message.author == self.user:
                return

            # ChatGPTの返答
            await self.chatgpt(message)
            return

        await self.check_trigger(message)
