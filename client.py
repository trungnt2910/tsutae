from datetime import datetime, timedelta
import discord
from discord import Embed, Message, TextChannel, Webhook
import typing
from typing import Self

from config import Config

class Client(discord.Client):
    def __init__(self, config: Config):
        super().__init__()
        self.config: Config = config
        self.__hooks: dict[TextChannel, Webhook] = {}

    def run(self: Self):
        super().run(self.config.token)

    async def __get_webhook(self: Self, target_channel: TextChannel) -> Webhook:
        target_webhook: Webhook | None = self.__hooks.get(target_channel)

        if target_webhook == None:
            for hook in await target_channel.webhooks():
                if hook.name == str(target_channel.id):
                    target_webhook = hook
                    break
            if target_webhook == None:
                target_webhook = await target_channel.create_webhook(
                    name = str(target_channel.id),
                    reason = f"伝え")

            self.__hooks[target_channel] = target_webhook

        return target_webhook

    @staticmethod
    async def __forward(target_webhook: Webhook, message: Message):
        if len(message.content) <= 2000:
            await target_webhook.send(
                content = message.content,
                username = message.author.display_name,
                avatar_url = message.author.display_avatar.url,
                embeds = message.embeds + [
                    Embed(
                        title = message.author.name,
                        url = message.jump_url,
                        description = "Forwarded by 伝え",
                        timestamp = message.created_at
                    )
                ],
                files = [ await a.to_file() for a in message.attachments ]
            )
        else:
            await target_webhook.send(
                content = message.content[0:2000],
                username = message.author.display_name,
                avatar_url = message.author.display_avatar.url,
                embeds = message.embeds + [
                    Embed(
                        title = message.author.name,
                        url = message.jump_url,
                        description = "Forwarded by 伝え (Part 1)",
                        timestamp = message.created_at
                    )
                ],
                files = [ await a.to_file() for a in message.attachments ]
            )
            await target_webhook.send(
                content = message.content[2000:-1],
                username = message.author.display_name,
                avatar_url = message.author.display_avatar.url,
                embeds = message.embeds + [
                    Embed(
                        title = message.author.name,
                        url = message.jump_url,
                        description = "Forwarded by 伝え (Part 2)",
                        timestamp = message.created_at
                    )
                ],
                files = [ await a.to_file() for a in message.attachments ]
            )

        print("Forwarded.")

    async def on_ready(self: Self):
        print(f'Logged on as {self.user}!')

        for channel_id in self.config.channels.keys():
            channel = \
                typing.cast(TextChannel, self.get_channel(int(channel_id)))

            target_channel = \
                typing.cast(TextChannel, self.get_channel(int(self.config.channels[channel_id])))

            messages = [
                m async for m in channel.history(
                    before = datetime.now(),
                    after = datetime.now() - timedelta(hours = self.config.history_age),
                    oldest_first = True
            ) ]

            if len(messages) < self.config.history_limit:
                messages = [
                    m async for m in channel.history(limit = self.config.history_limit)
                ]

            target_messages = [
                m async for m in target_channel.history(
                    before = datetime.now(),
                    after = datetime.now() - timedelta(hours = self.config.history_age),
                    oldest_first = True
                )
            ]

            for message in messages:
                found: bool = False
                for target_message in target_messages:
                    if len(target_message.embeds) == 0:
                        continue
                    if target_message.embeds[-1].url == message.jump_url:
                        found = True
                        break
                if not found:
                    print("A message has not been forwarded. Forwarding it now...")
                    await self.__forward(await self.__get_webhook(target_channel), message)

    async def on_message(self: Self, message: Message):
        if str(message.channel.id) in self.config.channels:
            target_channel = \
                typing.cast(TextChannel, self.get_channel(int(self.config.channels[str(message.channel.id)])))

            target_webhook = await self.__get_webhook(target_channel)
            await self.__forward(target_webhook, message)
