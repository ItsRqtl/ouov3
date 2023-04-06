"""
The cog module for the info commands.

This file is part of ouoteam/ouov3 which is released under GNU General Public License v3.0.
See file LISENCE for full license details.
"""

from typing import Union

import discord
from discord.ext import commands


class Info(commands.Cog):
    """
    Info commands cog.

    :param bot: The bot instance.
    :type bot: discord.AutoShardedBot
    """

    def __init__(self, bot: discord.AutoShardedBot) -> None:
        self.bot = bot

    info = discord.SlashCommandGroup("info", "查詢資訊", guild_only=True)

    @info.command(
        descrtiption="View bot information",
        description_localizations={"zh-TW": "查看機器人資訊", "zh-CN": "查看机器人信息"},
    )
    async def bot(self, ctx: discord.ApplicationContext) -> discord.Message:
        """
        Slash command to view the bot's information.

        :param ctx: The context of the slash command.
        :type ctx: discord.ApplicationContext

        :return: The message sent.
        :rtype: discord.Message
        """
        raise NotImplementedError("This command is not implemented yet.")

    @info.command(
        description="View user information",
        description_localizations={"zh-TW": "查看用戶資訊", "zh-CN": "查看用户信息"},
    )
    @discord.option(
        name="user",
        name_localizations={"zh-TW": "用戶", "zh-CN": "用户"},
        description="The user to view information of.",
        description_localizations={"zh-TW": "要查詢的用戶", "zh-CN": "要查询的用户"},
        input_type=discord.SlashCommandOptionType.user,
    )
    async def user(
        self, ctx: discord.ApplicationContext, user: Union[discord.Member, discord.User] = None
    ) -> discord.Message:
        """
        Slash command to view the user's information.

        :param ctx: The context of the slash command.
        :type ctx: discord.ApplicationContext
        :param user: The user to view information of.
        :type user: Union[discord.Member, discord.User]

        :return: The message sent.
        :rtype: discord.Message
        """
        if not user:
            user = ctx.author
        if isinstance(user, discord.User):
            ...  # Do something with a user
        elif isinstance(user, discord.Member):
            ...  # Do something with a member
        raise NotImplementedError("This command is not implemented yet.")

    @discord.user_command(
        name="User Info",
        name_localizations={"zh-TW": "用戶資訊", "zh-CN": "用户信息"},
        description="View user information",
        description_localizations={"zh-TW": "查看用戶資訊", "zh-CN": "查看用户信息"},
        guild_only=True,
    )
    async def user_command(
        self, ctx: discord.ApplicationContext, user: Union[discord.Member, discord.User] = None
    ) -> discord.Message:
        """
        User command to view the user's information.

        :param ctx: The context of the user command.
        :type ctx: discord.ApplicationContext
        :param user: The user to view information of.
        :type user: Union[discord.Member, discord.User]

        :return: The message sent.
        :rtype: discord.Message
        """
        return await self.user(ctx, user)

    @info.command(
        description="View guild information",
        description_localizations={"zh-TW": "查看伺服器資訊", "zh-CN": "查看服务器信息"},
    )
    async def guild(self, ctx: discord.ApplicationContext) -> discord.Message:
        """
        Slash command to view the guild's information.

        :param ctx: The context of the slash command.
        :type ctx: discord.ApplicationContext

        :return: The message sent.
        :rtype: discord.Message
        """
        raise NotImplementedError("This command is not implemented yet.")


def setup(bot: discord.AutoShardedBot) -> None:
    """
    The setup function for the cog.

    :param bot: The bot instance.
    :type bot: discord.AutoShardedBot
    """
    bot.add_cog(Info(bot))
