"""
The cog module for the Wikipedia commands.

This file is part of ouoteam/ouov3 which is released under GNU General Public License v3.0.
See file LISENCE for full license details.
"""

from urllib.parse import quote

import discord
from discord.ext import commands

from utils.embed import Embed
from utils.i18n import I18n
from utils.utils import Utils


class Wikipedia(commands.Cog):
    """
    Wikipedia searching commands.

    :param bot: The bot instance.
    :type bot: discord.AutoShardedBot
    """

    wiki = discord.SlashCommandGroup("wiki", "Search Wikipedia.")

    def __init__(self, bot: discord.AutoShardedBot) -> None:
        self.bot = bot

    @wiki.command(
        description="Go to a Wikipedia page.",
        description_localizations={"zh-TW": "前往維基百科頁面", "zh-CN": "前往维基百科页面"},
    )
    @discord.option(
        name="query",
        description="The page to go to.",
        description_localizations={"zh-TW": "要前往的頁面", "zh-CN": "要前往的页面"},
        required=True,
    )
    async def page(self, ctx: discord.ApplicationContext, query: str) -> discord.Message:
        """
        Go to a Wikipedia page.

        :param ctx: The context of the command.
        :type ctx: discord.ApplicationContext
        :param query: The page to go to.
        :type query: str

        :return: The reponse message.
        :rtype: discord.Message
        """
        await ctx.defer()
        data = await Utils.api_request(
            I18n.get(
                "wiki.api.url", ctx.locale or ctx.guild_locale, query=quote(query.replace(" ", "_"))
            ),
            {
                "accept-language": I18n.get(
                    "wiki.api.accept_language", ctx.locale or ctx.guild_locale
                ),
                "accept": 'application/json; charset=utf-8; profile="https://www.mediawiki.org/wiki/Specs/Summary/1.4.2"',
            },
        )
        if not data:
            return await ctx.respond(
                embed=Embed.error(I18n.get("wiki.page.no_result", ctx.locale or ctx.guild_locale))
            )
        if data["type"] == "disambiguation":
            description = I18n.get(
                "wiki.page.disambiguation.description", ctx.locale or ctx.guild_locale
            )
            author = I18n.get("wiki.page.disambiguation.author", ctx.locale or ctx.guild_locale)
        else:
            description = data["extract"]
            author = I18n.get("wiki.page.author", ctx.locale or ctx.guild_locale)
        embed = discord.Embed(
            title=data["title"],
            description=description,
            url=data["content_urls"]["desktop"]["page"],
            color=Embed.invisible(),
        ).set_author(
            name=author,
            url=I18n.get("wiki.url", ctx.locale or ctx.guild_locale),
            icon_url="https://www.wikipedia.org/portal/wikipedia.org/assets/img/Wikipedia-logo-v2.png",
        )
        if "thumbnail" in data:
            embed.set_image(url=data["thumbnail"]["source"])
        view = discord.ui.View(
            discord.ui.Button(
                style=discord.ButtonStyle.link,
                label=I18n.get("wiki.page.button", ctx.locale or ctx.guild_locale),
                url=data["content_urls"]["desktop"]["page"],
            )
        )
        await ctx.respond(embed=embed, view=view)

    @wiki.command(
        description="Show a random Wikipedia page.",
        description_localizations={"zh-TW": "顯示一個隨機的維基百科頁面", "zh-CN": "显示一个随机的维基百科页面"},
    )
    async def random(self, ctx: discord.ApplicationContext) -> discord.Message:
        """
        Show a random Wikipedia page.

        :param ctx: The context of the command.
        :type ctx: discord.ApplicationContext

        :return: The reponse message.
        :rtype: discord.Message
        """
        await ctx.defer()
        data = await Utils.api_request(
            I18n.get("wiki.api.random_url", ctx.locale or ctx.guild_locale),
            {
                "accept-language": I18n.get(
                    "wiki.api.accept_language", ctx.locale or ctx.guild_locale
                ),
                "accept": 'application/problem+json"',
            },
        )
        embed = discord.Embed(
            title=data["title"],
            description=data["extract"],
            url=data["content_urls"]["desktop"]["page"],
            color=Embed.invisible(),
        ).set_author(
            name=I18n.get("wiki.page.random.author", ctx.locale or ctx.guild_locale),
            url=I18n.get("wiki.url", ctx.locale or ctx.guild_locale),
            icon_url="https://www.wikipedia.org/portal/wikipedia.org/assets/img/Wikipedia-logo-v2.png",
        )
        if "thumbnail" in data:
            embed.set_image(url=data["thumbnail"]["source"])
        view = discord.ui.View(
            discord.ui.Button(
                style=discord.ButtonStyle.link,
                label=I18n.get("wiki.page.button", ctx.locale or ctx.guild_locale),
                url=data["content_urls"]["desktop"]["page"],
            )
        )
        await ctx.respond(embed=embed, view=view)


def setup(bot: discord.AutoShardedBot) -> None:
    """
    The setup function for the cog.

    :param bot: The bot instance.
    :type bot: discord.AutoShardedBot
    """
    bot.add_cog(Wikipedia(bot))
