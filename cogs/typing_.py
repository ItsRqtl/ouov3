"""
The cog module for the typing commands and tasks.

This file is part of ouoteam/ouov3 which is released under GNU General Public License v3.0.
See file LISENCE for full license details.
"""

from typing import Union

import aiofiles
import discord
import orjson
from discord.ext import commands, tasks

from utils.embed import Embed
from utils.i18n import I18n


class Typing(commands.Cog):
    """
    Typing commands and tasks cog.

    :param bot: The bot instance.
    :type bot: discord.AutoShardedBot
    """

    def __init__(self, bot: discord.AutoShardedBot) -> None:
        self.bot = bot
        self._channels = None
        self.typing_task.start()

    @tasks.loop(seconds=5)
    async def typing_task(self) -> None:
        """
        The typing task.
        """
        if self._channels is None:
            async with aiofiles.open("data/typing.json", "rb") as f:
                self._channels = orjson.loads(await f.read())
        for c in self._channels:
            try:
                if channel := self.bot.get_channel(c):
                    await channel.trigger_typing()
            except Exception:
                self._channels.remove(c)
                async with aiofiles.open("data/typing.json", "wb") as f:
                    await f.write(orjson.dumps(self._channels))

    typing = discord.SlashCommandGroup(
        "typing",
        "輸入中",
        guild_only=True,
        default_member_permissions=discord.Permissions(manage_channels=True),
    )

    @typing.command(
        description="Start typing in a channel.",
        description_localizations={"zh-TW": "在頻道中開始輸入", "zh-CN": "在频道中开始输入"},
    )
    @discord.option(
        name="channel",
        name_localizations={"zh-TW": "頻道", "zh-CN": "频道"},
        description="The channel to start typing in.",
        description_localizations={"zh-TW": "要開始輸入的頻道", "zh-CN": "要开始输入的频道"},
        channel_types=[
            discord.ChannelType.text,
            discord.ChannelType.news,
            discord.ChannelType.news_thread,
            discord.ChannelType.public_thread,
            discord.ChannelType.private_thread,
            discord.ChannelType.voice,
        ],
    )
    async def start(
        self,
        ctx: discord.ApplicationContext,
        channel: Union[discord.TextChannel, discord.VoiceChannel, discord.Thread],
    ) -> discord.Message:
        """
        Slash command to add a channel to the typing task.

        :param ctx: The context of the slash command.
        :type ctx: discord.ApplicationContext
        :param channel: The channel to add to the typing task.
        :type channel: Union[discord.TextChannel, discord.VoiceChannel, discord.Thread]

        :return: The message sent.
        :rtype: discord.Message
        """
        await ctx.defer(ephemeral=True)
        if not channel.permissions_for(ctx.guild.me).send_messages:
            return await ctx.respond(
                embed=Embed.error(
                    I18n.get(
                        "typing.start.no_permission",
                        ctx.locale or ctx.guild_locale,
                        channel=channel.mention,
                    )
                )
            )
        if channel.id in self._channels:
            msg = await ctx.respond(
                embed=Embed.error(
                    I18n.get(
                        "typing.start.already_typing",
                        ctx.locale or ctx.guild_locale,
                        channel=channel.mention,
                    )
                )
            )
        else:
            self._channels.append(channel.id)
            async with aiofiles.open("data/typing.json", "wb") as f:
                await f.write(orjson.dumps(self._channels))
            msg = await ctx.respond(
                I18n.get(
                    "typing.start.typing", ctx.locale or ctx.guild_locale, channel=channel.mention
                )
            )
        await channel.trigger_typing()
        return msg

    @typing.command(
        description="Stop typing in a channel.",
        description_localizations={"zh-TW": "在頻道中停止輸入", "zh-CN": "在频道中停止输入"},
    )
    @discord.option(
        name="channel",
        name_localizations={"zh-TW": "頻道", "zh-CN": "频道"},
        description="The channel to stop typing in.",
        description_localizations={"zh-TW": "要停止輸入的頻道", "zh-CN": "要停止输入的频道"},
        channel_types=[
            discord.ChannelType.text,
            discord.ChannelType.news,
            discord.ChannelType.news_thread,
            discord.ChannelType.public_thread,
            discord.ChannelType.private_thread,
            discord.ChannelType.voice,
        ],
    )
    async def stop(
        self,
        ctx: discord.ApplicationContext,
        channel: Union[discord.TextChannel, discord.VoiceChannel, discord.Thread],
    ) -> discord.Message:
        """
        Slash command to remove a channel from the typing task.

        :param ctx: The context of the slash command.
        :type ctx: discord.ApplicationContext
        :param channel: The channel to remove from the typing task.
        :type channel: Union[discord.TextChannel, discord.VoiceChannel, discord.Thread]

        :return: The message sent.
        :rtype: discord.Message
        """
        await ctx.defer(ephemeral=True)
        if channel.id not in self._channels:
            return await ctx.respond(
                embed=Embed.error(
                    I18n.get(
                        "typing.stop.not_typing",
                        ctx.locale or ctx.guild_locale,
                        channel=channel.mention,
                    )
                )
            )
        self._channels.remove(channel.id)
        async with aiofiles.open("data/typing.json", "wb") as f:
            await f.write(orjson.dumps(self._channels))
        return await ctx.respond(
            I18n.get("typing.stop.typing", ctx.locale or ctx.guild_locale, channel=channel.mention)
        )


def setup(bot: discord.AutoShardedBot) -> None:
    """
    The setup function for the cog.

    :param bot: The bot instance.
    :type bot: discord.AutoShardedBot
    """
    bot.add_cog(Typing(bot))
