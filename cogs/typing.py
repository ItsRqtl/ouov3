"""
The cog module for the typing commands and tasks.
"""

from typing import Union

import discord
from discord.ext import commands, tasks


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
            self._channels = []
            ...  # fetch channels from database
        for c in self._channels:
            try:
                if channel := self.bot.get_channel(c):
                    await channel.trigger_typing()
            except Exception:
                self._channels.remove(c)
                ...  # remove channel from database

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
                f"I don't have permission to send messages in {channel.mention}.",
                # localizations={"zh-TW": f"我沒有在 {channel.mention} 中發送訊息的權限", "zh-CN": f"我没有在 {channel.mention} 中发送消息的权限"},
            )
        if channel.id in self._channels:
            msg = await ctx.respond(
                "Already typing in that channel.",
                # localizations={"zh-TW": "已經在該頻道中輸入中", "zh-CN": "已经在该频道中输入中"},
            )
        else:
            self._channels.append(channel.id)
            ...  # save channel to database
            msg = await ctx.respond(
                f"Now typing in {channel.mention}.",
                # localizations={"zh-TW": f"開始在 {channel.mention} 輸入中", "zh-CN": f"开始在 {channel.mention} 输入中"},
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
                "Not typing in that channel.",
                # localizations={"zh-TW": "不在該頻道中輸入中", "zh-CN": "不在该频道中输入中"},
            )
        self._channels.remove(channel.id)
        ...  # remove channel from database
        return await ctx.respond(
            f"No longer typing in {channel.mention}.",
            # localizations={"zh-TW": f"不再在 {channel.mention} 輸入中", "zh-CN": f"不再在 {channel.mention} 输入中"},
        )


def setup(bot: discord.AutoShardedBot) -> None:
    """
    The setup function for the cog.

    :param bot: The bot instance.
    :type bot: discord.AutoShardedBot
    """
    bot.add_cog(Typing(bot))
