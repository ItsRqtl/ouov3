"""
The cog module for thread commands and events.

This file is part of ouoteam/ouov3 which is released under GNU General Public License v3.0.
See file LISENCE for full license details.
"""

import contextlib

import discord
from discord.ext import commands

from utils.embed import Embed
from utils.i18n import I18n


class Thread(commands.Cog):
    """
    Thread commands cog.

    :param bot: The bot instance.
    :type bot: discord.AutoShardedBot
    """

    thread = discord.SlashCommandGroup(
        "thread",
        "Thread commands.",
        default_member_permissions=discord.Permissions(manage_threads=True),
        guild_only=True,
    )

    def __init__(self, bot: discord.AutoShardedBot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_thread_create(self, thread: discord.Thread) -> None:
        """
        The event listener for thread creation.

        :param thread: The thread that was created.
        :type thread: discord.Thread
        """
        with contextlib.suppress(Exception):
            await thread.join()

    @thread.command(
        description="Archive the current thread.",
        description_localizations={"zh-TW": "封存目前的討論串", "zh-CN": "归档目前的讨论串"},
    )
    async def archive(self, ctx: discord.ApplicationContext) -> discord.Message:
        """
        Archive the current thread.

        :param ctx: The context of the slash command.
        :type ctx: discord.ApplicationContext

        :return: The response message.
        :rtype: discord.Message
        """
        await ctx.defer(ephemeral=True)
        if ctx.channel.type not in [
            discord.ChannelType.news_thread,
            discord.ChannelType.public_thread,
            discord.ChannelType.private_thread,
        ]:
            return await ctx.respond(
                embed=Embed.error(
                    I18n.get("thread.archive_not_thread", ctx.locale or ctx.guild_locale),
                )
            )
        msg = await ctx.respond(
            I18n.get("thread.archiving", ctx.locale or ctx.guild_locale),
        )
        try:
            await ctx.channel.edit(archived=True, locked=True)
        except Exception:
            msg = await ctx.followup.send(
                embed=Embed.error(
                    I18n.get("thread.archive_failed", ctx.locale or ctx.guild_locale)
                ),
                ephemeral=True,
            )
        return msg

    @thread.command(
        description="Add a user to the current thread.",
        description_localizations={"zh-TW": "將使用者加入目前的討論串", "zh-CN": "将用户加入目前的讨论串"},
    )
    @discord.option(
        name="user",
        description="The user to add to the thread.",
        description_localizations={"zh-TW": "要加入討論串的使用者", "zh-CN": "要加入讨论串的用户"},
    )
    async def add(self, ctx: discord.ApplicationContext, user: discord.Member) -> discord.Message:
        """
        Add a user to the current thread.

        :param ctx: The context of the slash command.
        :type ctx: discord.ApplicationContext
        :param user: The user to add to the thread.
        :type user: discord.Member

        :return: The response message.
        :rtype: discord.Message
        """
        await ctx.defer(ephemeral=True)
        if ctx.channel.type not in [
            discord.ChannelType.news_thread,
            discord.ChannelType.public_thread,
            discord.ChannelType.private_thread,
        ]:
            return await ctx.respond(
                embed=Embed.error(
                    I18n.get("thread.add_not_thread", ctx.locale or ctx.guild_locale),
                )
            )
        if user in ctx.channel.members:
            return await ctx.respond(
                embed=Embed.error(
                    I18n.get(
                        "thread.add_already_in", ctx.locale or ctx.guild_locale, [user.mention]
                    ),
                )
            )
        try:
            await ctx.channel.add_user(user)
        except Exception:
            return await ctx.respond(
                embed=Embed.error(
                    I18n.get("thread.add_failed", ctx.locale or ctx.guild_locale, [user.mention]),
                )
            )
        return await ctx.respond(
            embed=Embed.success(
                I18n.get("thread.add_success", ctx.locale or ctx.guild_locale, [user.mention]),
            )
        )

    @thread.command(
        description="Remove a user from the current thread.",
        description_localizations={"zh-TW": "將使用者從目前的討論串中移除", "zh-CN": "将用户从目前的讨论串中移除"},
    )
    @discord.option(
        name="user",
        description="The user to remove from the thread.",
        description_localizations={"zh-TW": "要從討論串中移除的使用者", "zh-CN": "要从讨论串中移除的用户"},
    )
    async def remove(
        self, ctx: discord.ApplicationContext, user: discord.Member
    ) -> discord.Message:
        """
        Remove a user from the current thread.

        :param ctx: The context of the slash command.
        :type ctx: discord.ApplicationContext
        :param user: The user to remove from the thread.
        :type user: discord.Member

        :return: The response message.
        :rtype: discord.Message
        """
        await ctx.defer(ephemeral=True)
        if ctx.channel.type not in [
            discord.ChannelType.news_thread,
            discord.ChannelType.public_thread,
            discord.ChannelType.private_thread,
        ]:
            return await ctx.respond(
                embed=Embed.error(
                    I18n.get("thread.remove_not_thread", ctx.locale or ctx.guild_locale),
                )
            )
        if user not in ctx.channel.members:
            return await ctx.respond(
                embed=Embed.error(
                    I18n.get(
                        "thread.remove_not_in", ctx.locale or ctx.guild_locale, [user.mention]
                    ),
                )
            )
        try:
            await ctx.channel.remove_user(user)
        except Exception:
            return await ctx.respond(
                embed=Embed.error(
                    I18n.get(
                        "thread.remove_failed", ctx.locale or ctx.guild_locale, [user.mention]
                    ),
                )
            )
        return await ctx.respond(
            embed=Embed.success(
                I18n.get("thread.remove_success", ctx.locale or ctx.guild_locale, [user.mention]),
            )
        )


def setup(bot: discord.AutoShardedBot) -> None:
    """
    The setup function for the cog.

    :param bot: The bot instance.
    :type bot: discord.AutoShardedBot
    """
    bot.add_cog(Thread(bot))
