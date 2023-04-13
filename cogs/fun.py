"""
The cog module for fun commands (or whatever not categorized lmfao)

This file is part of ouoteam/ouov3 which is released under GNU General Public License v3.0.
See file LISENCE for full license details.
"""

import datetime
from io import BytesIO, StringIO
from random import choice, randint
from urllib.parse import quote_plus

import aiofiles
import aiohttp
import discord
import orjson

from utils.embed import Color, Embed
from utils.i18n import I18n
from utils.logging import Cog
from utils.utils import Utils


class Fun(Cog):
    """
    Fun commands cog.

    :param bot: The bot instance.
    :type bot: discord.AutoShardedBot
    """

    def __init__(self, bot: discord.AutoShardedBot) -> None:
        self.bot = bot

    def generate_bullshit(self, topic: str, length: int, data: dict) -> str:
        """
        Generate bullshit.

        :param topic: The topic to generate bullshit about.
        :type topic: str
        :param length: The length of the bullshit.
        :type length: int

        :return: The generated bullshit.
        :rtype: str
        """
        generated = ""
        while len(generated) < length:
            _r = randint(0, 99)
            if _r < 2 and generated and generated[-1] in "。？！?!\n":
                sentence = "\n\n"
            elif _r < 25:
                sentence = (
                    choice(data["famous"])
                    .replace("[A]", choice(data["before"]))
                    .replace("[B]", choice(data["after"]))
                )
            else:
                sentence = choice(data["bullshit"]).replace("x", topic)
            if sentence == "\n\n" or sentence not in generated:
                generated += sentence
        if topic not in generated:
            return self.generate_bullshit(topic, length, data)
        return generated

    @discord.slash_command(
        description="Generate bullshit text.",
        description_localization={"zh-TW": "唬爛產生器", "zh-CN": "唬烂生成器"},
    )
    @discord.option(
        name="topic",
        description="The topic to generate bullshit about.",
        description_localization={"zh-TW": "要產生唬爛的主題。", "zh-CN": "要产生唬烂的主题。"},
    )
    @discord.option(
        name="length",
        description="The length of the bullshit.",
        description_localization={"zh-TW": "唬爛的長度。", "zh-CN": "唬烂的长度。"},
        min_value=50,
        max_value=50000,
    )
    async def bullshit(
        self, ctx: discord.ApplicationContext, topic: str, length: int = 250
    ) -> discord.Message:
        """
        The bullshit command.

        :param ctx: The context of the command.
        :type ctx: discord.ApplicationContext
        :param topic: The topic to generate bullshit about.
        :type topic: str
        :param length: The length of the bullshit.
        :type length: int

        :return: The response message.
        :rtype: discord.Message
        """
        await ctx.defer()
        async with aiofiles.open("assets/bullshit.json", "rb") as f:
            data = orjson.loads(await f.read())
        generated = self.generate_bullshit(topic, length, data)
        generated_length = len(generated)
        resp = I18n.get(
            "fun.bullshit.generated",
            ctx.locale or ctx.guild_locale,
            topic=topic,
            length=generated_length,
        )
        if generated_length > 4096:
            file = discord.File(StringIO(generated), filename="bs.txt")
            return await ctx.respond(resp, file=file)
        embed = discord.Embed(title=resp, description=generated, color=Color.random_color())
        return await ctx.respond(embed=embed)

    @discord.slash_command(
        description="Let me Google that for you.",
        description_localization={"zh-TW": "讓我幫你Google。", "zh-CN": "让我帮你Google。"},
    )
    @discord.option(
        name="search",
        description="The search content.",
        description_localization={"zh-TW": "搜尋內容。", "zh-CN": "搜索内容。"},
        max_length=200,
    )
    async def lmgtfy(self, ctx: discord.ApplicationContext, search: str) -> discord.Message:
        """
        The lmgtfy command.

        :param ctx: The context of the command.
        :type ctx: discord.ApplicationContext
        :param search: The search content.
        :type search: str

        :return: The response message.
        :rtype: discord.Message
        """
        await ctx.defer()
        return await ctx.respond(
            I18n.get(
                "fun.lmgtfy.generated", ctx.locale or ctx.guild_locale, query=quote_plus(search)
            )
        )

    # NO TRANSLATION/OUTPUT FORMAT: This is a meme command. #
    @discord.slash_command(description="You should try it and see!")
    async def tias(self, ctx: discord.ApplicationContext) -> discord.Message:
        """
        The tias command.

        :param ctx: The context of the command.
        :type ctx: discord.ApplicationContext

        :return: The response message.
        :rtype: discord.Message
        """
        await ctx.defer()
        return await ctx.respond("Just [try it and see!](https://tryitands.ee/)")

    @discord.slash_command(
        description="Generate a random number.",
        description_localization={"zh-TW": "隨機產生一個數字。", "zh-CN": "随机产生一个数字。"},
    )
    @discord.option(
        name="min",
        name_localization={"zh-TW": "從", "zh-CN": "从"},
        description="The minimum value.",
        description_localization={"zh-TW": "最小值。", "zh-CN": "最小值。"},
        min_value=0,
    )
    @discord.option(
        name="max",
        name_localization={"zh-TW": "到", "zh-CN": "到"},
        description="The maximum value.",
        description_localization={"zh-TW": "最大值。", "zh-CN": "最大值。"},
        min_value=0,
    )
    async def random(self, ctx: discord.ApplicationContext, min: int, max: int) -> discord.Message:
        """
        The random command.

        :param ctx: The context of the command.
        :type ctx: discord.ApplicationContext
        :param min: The minimum value.
        :type min: int
        :param max: The maximum value.
        :type max: int

        :return: The response message.
        :rtype: discord.Message
        """
        await ctx.defer()
        if min == max:
            return await ctx.respond(
                embed=Embed.error(I18n.get("fun.random.no_range", ctx.locale or ctx.guild_locale))
            )
        if min > max:
            min, max = max, min
        result = randint(min, max)
        return await ctx.respond(
            I18n.get(
                "fun.random.generated",
                ctx.locale or ctx.guild_locale,
                min=min,
                max=max,
                result=result,
            )
        )

    @discord.slash_command(
        description="Look up an anime by its screenshot.",
        description_localization={"zh-TW": "查詢動畫截圖。", "zh-CN": "查询动画截图。"},
    )
    @discord.option(
        name="image",
        description="The screenshot of the anime.",
        description_localization={"zh-TW": "動畫截圖。", "zh-CN": "动画截图。"},
    )
    async def whatanime(
        self, ctx: discord.ApplicationContext, image: discord.Attachment
    ) -> discord.Message:
        """
        The whatanime command.

        :param ctx: The context of the command.
        :type ctx: discord.ApplicationContext
        :param image: The screenshot of the anime.
        :type image: discord.Attachment

        :return: The response message.
        :rtype: discord.Message
        """
        await ctx.defer()
        if "image" not in image.content_type:
            return await ctx.respond(
                embed=Embed.error(
                    I18n.get("fun.whatanime.not_image", ctx.locale or ctx.guild_locale)
                )
            )
        url = await Utils.api_request(f"https://api.trace.moe/search?url={quote_plus(image.url)}")
        if url == 429:
            return await ctx.respond(
                embed=Embed.error(
                    I18n.get("fun.whatanime.rate_limited", ctx.locale or ctx.guild_locale)
                )
            )
        if url == 402:
            return await ctx.respond(
                embed=Embed.error(
                    I18n.get("fun.whatanime.no_quota", ctx.locale or ctx.guild_locale)
                )
            )
        if url["result"][0]["similarity"] < 0.9:
            return await ctx.respond(
                embed=Embed.error(
                    I18n.get("fun.whatanime.no_result", ctx.locale or ctx.guild_locale)
                )
            )
        async with aiohttp.ClientSession() as s, s.post(
            "https://trace.moe/anilist/",
            json={
                "query": "query ($id: Int) {Media (id: $id, type: ANIME) {id\nsiteUrl\ntitle {native}}}",
                "variables": {"id": url["result"][0]["anilist"]},
            },
        ) as r:
            resp = await r.json()
        async with aiohttp.ClientSession() as s, s.get(f"{url['result'][0]['image']}&size=l") as r:
            preview = BytesIO(await r.content.read())
        embed = discord.Embed(
            title=resp["data"]["Media"]["title"]["native"],
            description=I18n.get(
                "fun.whatanime.result",
                ctx.locale or ctx.guild_locale,
                title=resp["data"]["Media"]["title"]["chinese"] or "N/A",
                episode=url["result"][0]["episode"] or "N/A",
                time=f"{datetime.timedelta(seconds=int(url['result'][0]['from']))} - {datetime.timedelta(seconds=int(url['result'][0]['to']))}",
                similarity=round(url["result"][0]["similarity"] * 100, 2),
            ),
            color=Color.random_color(),
        )
        embed.set_image(url="attachment://preview.jpg")
        embed.set_footer(text=I18n.get("fun.whatanime.footer", ctx.locale or ctx.guild_locale))
        await ctx.respond(embed=embed, file=discord.File(filename="preview.jpg", fp=preview))


def setup(bot: discord.AutoShardedBot) -> None:
    """
    The setup function for the cog.

    :param bot: The bot instance.
    :type bot: discord.AutoShardedBot
    """
    bot.add_cog(Fun(bot))
