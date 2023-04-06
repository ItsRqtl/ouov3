"""
The cog module for the rtfd commands.
"""

from typing import List, Union
from urllib.parse import quote

import discord
from discord.ext import commands, pages

from utils.embed import Embed
from utils.i18n import I18n
from utils.utils import Utils


class Rtfd(commands.Cog):
    """
    Docs searching commands.

    :param bot: The bot instance.
    :type bot: discord.AutoShardedBot
    """

    vaild_projects = ["interactionspy", "discordpy", "pycord", "disnake", "nextcord"]

    def __init__(self, bot: discord.AutoShardedBot) -> None:
        self.bot = bot

    def escape_md(str: str) -> str:
        """
        Escape markdown for discord.

        :param str: The string to escape.
        :type str: str

        :return: The escaped string.
        :rtype: str
        """
        return str.replace("*", "\\*").replace("_", "\\_").replace("`", "\\`").replace("~", "\\~")

    @classmethod
    def get_embeds(
        cls, data: dict, name: str, url: str, icon: str, locale: str
    ) -> List[discord.Embed]:
        """
        Return a list of Embeds from the given data.

        :param data: The data to convert.
        :type data: dict
        :param name: The name of the library.
        :type name: str
        :param url: The url of the library.
        :type url: str
        :param icon: The icon of the library.
        :type icon: str
        :param locale: The locale of the response.
        :type locale: str

        :return: The list of Embeds.
        :rtype: List[discord.Embed]
        """
        results = []
        link_text = I18n.get("rtfd.link_text", locale)
        for i in data["results"]:
            if i["project"] not in cls.vaild_projects:
                continue
            eb = discord.Embed(title=i["title"], url=f"""{i["domain"]}{i["path"]}""")
            eb.set_author(name=name, url=url, icon_url=icon)
            for j in i["blocks"]:
                if j["type"] == "domain":
                    content = cls.escape_md(j["content"])
                    link = f"""\n[[{link_text}]({i["domain"]}{i["path"]}#{j["id"]})]"""
                    if len(content) + len(link) > 1024:
                        content = f"{content[:1020 - len(link)]}..."
                    content += link
                    eb.add_field(name=j["name"], value=content)
            if eb.fields:
                results.append(eb)
        return results

    rtfd = discord.SlashCommandGroup("rtfd", "Search the docs for a specific query.")

    pycord = rtfd.create_subgroup(
        "pycord",
        "Search the Pycord docs for a specific query.",
    )

    @pycord.command(
        name="search",
        description="Search the Pycord docs for a specific query.",
        description_localizations={"zh-TW": "在 Pycord 文檔中搜尋", "zh-CN": "在 Pycord 文档中搜索"},
    )
    @discord.option(
        name="query",
        description="The query to search for.",
        description_localizations={"zh-TW": "要搜尋的內容", "zh-CN": "要搜索的内容"},
    )
    async def pycord_search(
        self, ctx: discord.ApplicationContext, query: str
    ) -> Union[discord.Message, discord.WebhookMessage]:
        """
        Search the Pycord docs for a specific query.

        :param ctx: The context of the command.
        :type ctx: discord.ApplicationContext
        :param query: The query to search for.
        :type query: str

        :return: The message sent.
        :rtype: Union[discord.Message, discord.WebhookMessage]
        """
        await ctx.defer()
        data = await Utils.api_request(
            f"https://docs.pycord.dev/_/api/v2/search/?q={quote(query)}&project=pycord&version=stable&language=en"
        )
        results = Rtfd.get_embeds(
            data,
            "Pycord",
            "https://docs.pycord.dev/en/stable/",
            "https://avatars.githubusercontent.com/u/89700626?s=200&v=4",
            ctx.locale or ctx.guild_locale,
        )
        if not results:
            return await ctx.respond(
                embed=Embed.error(
                    I18n.get("docs.no_results", ctx.locale or ctx.guild_locale),
                )
            )
        elif len(results) == 1:
            return await ctx.respond(embed=results[0])
        else:
            paginator = pages.Paginator(results)
            return await paginator.respond(ctx.interaction)

    @pycord.command(
        name="docs",
        description="Get the link to the Pycord docs.",
        description_localizations={"zh-TW": "取得 Pycord 文檔的連結", "zh-CN": "获取 Pycord 文档的链接"},
    )
    async def pycord_docs(self, ctx: discord.ApplicationContext) -> discord.Message:
        """
        Get the link to the Pycord docs.

        :param ctx: The context of the command.
        :type ctx: discord.ApplicationContext

        :return: The message sent.
        :rtype: discord.Message
        """
        await ctx.defer()
        return await ctx.respond("https://docs.pycord.dev/en/stable/")

    dpy = rtfd.create_subgroup(
        "dpy",
        "Search the discord.py docs for a specific query.",
    )

    @dpy.command(
        name="search",
        description="Search the discord.py docs for a specific query.",
        description_localizations={"zh-TW": "在 discord.py 文檔中搜尋", "zh-CN": "在 discord.py 文档中搜索"},
    )
    @discord.option(
        name="query",
        description="The query to search for.",
        description_localizations={"zh-TW": "要搜尋的內容", "zh-CN": "要搜索的内容"},
    )
    async def dpy_search(
        self, ctx: discord.ApplicationContext, query: str
    ) -> Union[discord.Message, discord.WebhookMessage]:
        """
        Search the discord.py docs for a specific query.

        :param ctx: The context of the command.
        :type ctx: discord.ApplicationContext
        :param query: The query to search for.
        :type query: str

        :return: The message sent.
        :rtype: Union[discord.Message, discord.WebhookMessage]
        """
        await ctx.defer()
        data = await Utils.api_request(
            f"https://discordpy.readthedocs.io/_/api/v2/search/?q={quote(query)}&project=discordpy&version=stable&language=en"
        )
        results = Rtfd.get_embeds(
            data,
            "discord.py",
            "https://discordpy.readthedocs.io/en/stable/",
            "https://truth.bahamut.com.tw/s01/202106/f394bbeb4bfac8abdfafe49dbfd0427d.PNG",
            ctx.locale or ctx.guild_locale,
        )
        if not results:
            return await ctx.respond(
                embed=Embed.error(
                    I18n.get("docs.no_results", ctx.locale or ctx.guild_locale),
                )
            )
        elif len(results) == 1:
            return await ctx.respond(embed=results[0])
        else:
            paginator = pages.Paginator(results)
            return await paginator.respond(ctx.interaction)

    @dpy.command(
        name="docs",
        description="Get the link to the discord.py docs.",
        description_localizations={"zh-TW": "取得 discord.py 文檔的連結", "zh-CN": "获取 discord.py 文档的链接"},
    )
    async def dpy_docs(self, ctx: discord.ApplicationContext) -> discord.Message:
        """
        Get the link to the discord.py docs.

        :param ctx: The context of the command.
        :type ctx: discord.ApplicationContext

        :return: The message sent.
        :rtype: discord.Message
        """
        await ctx.defer()
        return await ctx.respond("https://discordpy.readthedocs.io/en/stable/")

    ipy = rtfd.create_subgroup(
        "ipy",
        "Search the interactions.py docs for a specific query.",
    )

    @ipy.command(
        name="search",
        description="Search the interactions.py docs for a specific query.",
        description_localizations={
            "zh-TW": "在 interactions.py 文檔中搜尋",
            "zh-CN": "在 interactions.py 文档中搜索",
        },
    )
    @discord.option(
        name="query",
        description="The query to search for.",
        description_localizations={"zh-TW": "要搜尋的內容", "zh-CN": "要搜索的内容"},
    )
    async def ipy_search(
        self, ctx: discord.ApplicationContext, query: str
    ) -> Union[discord.Message, discord.WebhookMessage]:
        """
        Search the interactions.py docs for a specific query.

        :param ctx: The context of the command.
        :type ctx: discord.ApplicationContext
        :param query: The query to search for.
        :type query: str

        :return: The message sent.
        :rtype: Union[discord.Message, discord.WebhookMessage]
        """
        await ctx.defer()
        data = await Utils.api_request(
            f"https://interactionspy.readthedocs.io/_/api/v2/search/?q={quote(query)}&project=interactionspy&version=latest&language=en"
        )
        results = Rtfd.get_embeds(
            data,
            "interactions.py",
            "https://interactionspy.readthedocs.io/en/latest/",
            "https://avatars.githubusercontent.com/u/98242689?s=200&v=4",
            ctx.locale or ctx.guild_locale,
        )
        if not results:
            return await ctx.respond(
                embed=Embed.error(
                    I18n.get("docs.no_results", ctx.locale or ctx.guild_locale),
                )
            )
        elif len(results) == 1:
            return await ctx.respond(embed=results[0])
        else:
            paginator = pages.Paginator(results)
            return await paginator.respond(ctx.interaction)

    @ipy.command(
        name="docs",
        description="Get the link to the interactions.py docs.",
        description_localizations={
            "zh-TW": "取得 interactions.py 文檔的連結",
            "zh-CN": "获取 interactions.py 文档的链接",
        },
    )
    async def ipy_docs(self, ctx: discord.ApplicationContext) -> discord.Message:
        """
        Get the link to the interactions.py docs.

        :param ctx: The context of the command.
        :type ctx: discord.ApplicationContext

        :return: The message sent.
        :rtype: discord.Message
        """
        await ctx.defer()
        return await ctx.respond("https://interactionspy.readthedocs.io/en/latest/")

    nextcord = rtfd.create_subgroup(
        "nextcord",
        "Search the nextcord docs for a specific query.",
    )

    @nextcord.command(
        name="search",
        description="Search the nextcord docs for a specific query.",
        description_localizations={"zh-TW": "在 nextcord 文檔中搜尋", "zh-CN": "在 nextcord 文档中搜索"},
    )
    @discord.option(
        name="query",
        description="The query to search for.",
        description_localizations={"zh-TW": "要搜尋的內容", "zh-CN": "要搜索的内容"},
    )
    async def nextcord_search(
        self, ctx: discord.ApplicationContext, query: str
    ) -> Union[discord.Message, discord.WebhookMessage]:
        """
        Search the nextcord docs for a specific query.

        :param ctx: The context of the command.
        :type ctx: discord.ApplicationContext
        :param query: The query to search for.
        :type query: str

        :return: The message sent.
        :rtype: Union[discord.Message, discord.WebhookMessage]
        """
        await ctx.defer()
        data = await Utils.api_request(
            f"https://docs.nextcord.dev/_/api/v2/search/?q={quote(query)}&project=nextcord&version=latest&language=en"
        )
        results = Rtfd.get_embeds(
            data,
            "nextcord",
            "https://docs.nextcord.dev/en/stable/",
            "https://avatars.githubusercontent.com/u/89693200?s=200&v=4",
            ctx.locale or ctx.guild_locale,
        )
        if not results:
            return await ctx.respond(
                embed=Embed.error(
                    I18n.get("docs.no_results", ctx.locale or ctx.guild_locale),
                )
            )
        elif len(results) == 1:
            return await ctx.respond(embed=results[0])
        else:
            paginator = pages.Paginator(results)
            return await paginator.respond(ctx.interaction)

    @nextcord.command(
        name="docs",
        description="Get the link to the nextcord docs.",
        description_localizations={"zh-TW": "取得 nextcord 文檔的連結", "zh-CN": "获取 nextcord 文档的链接"},
    )
    async def nextcord_docs(self, ctx: discord.ApplicationContext) -> discord.Message:
        """
        Get the link to the nextcord docs.

        :param ctx: The context of the command.
        :type ctx: discord.ApplicationContext

        :return: The message sent.
        :rtype: discord.Message
        """
        await ctx.defer()
        return await ctx.respond("https://docs.nextcord.dev/en/stable/")

    disnake = rtfd.create_subgroup(
        "disnake",
        "Search the disnake docs for a specific query.",
    )

    @disnake.command(
        name="search",
        description="Search the disnake docs for a specific query.",
        description_localizations={"zh-TW": "在 disnake 文檔中搜尋", "zh-CN": "在 disnake 文档中搜索"},
    )
    @discord.option(
        name="query",
        description="The query to search for.",
        description_localizations={"zh-TW": "要搜尋的內容", "zh-CN": "要搜索的内容"},
    )
    async def disnake_search(
        self, ctx: discord.ApplicationContext, query: str
    ) -> Union[discord.Message, discord.WebhookMessage]:
        """
        Search the disnake docs for a specific query.

        :param ctx: The context of the command.
        :type ctx: discord.ApplicationContext
        :param query: The query to search for.
        :type query: str

        :return: The message sent.
        :rtype: Union[discord.Message, discord.WebhookMessage]
        """
        await ctx.defer()
        data = await Utils.api_request(
            f"https://docs.disnake.dev/_/api/v2/search/?q={quote(query)}&project=disnake&version=latest&language=en"
        )
        results = Rtfd.get_embeds(
            data,
            "disnake",
            "https://disnake.readthedocs.io/en/latest/",
            "https://avatars.githubusercontent.com/u/93640097?s=200&v=4",
            ctx.locale or ctx.guild_locale,
        )
        if not results:
            return await ctx.respond(
                embed=Embed.error(
                    I18n.get("docs.no_results", ctx.locale or ctx.guild_locale),
                )
            )
        elif len(results) == 1:
            return await ctx.respond(embed=results[0])
        else:
            paginator = pages.Paginator(results)
            return await paginator.respond(ctx.interaction)

    @disnake.command(
        name="docs",
        description="Get the link to the disnake docs.",
        description_localizations={"zh-TW": "取得 disnake 文檔的連結", "zh-CN": "获取 disnake 文档的链接"},
    )
    async def disnake_docs(self, ctx: discord.ApplicationContext) -> discord.Message:
        """
        Get the link to the disnake docs.

        :param ctx: The context of the command.
        :type ctx: discord.ApplicationContext

        :return: The message sent.
        :rtype: discord.Message
        """
        await ctx.defer()
        return await ctx.respond("https://docs.disnake.dev/en/stable/")


def setup(bot: discord.AutoShardedBot) -> None:
    """
    The setup function for the cog.

    :param bot: The bot instance.
    :type bot: discord.AutoShardedBot
    """
    bot.add_cog(Rtfd(bot))
