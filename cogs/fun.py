"""
The cog module for fun commands (or whatever not categorized lmfao)
"""

from io import StringIO
from random import choice, randint

import aiofiles
import discord
import orjson
from discord.ext import commands

from utils.i18n import I18n


class Fun(commands.Cog):
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
        await ctx.defer(ephemeral=True)
        async with aiofiles.open("assets/bullshit.json", "rb") as f:
            data = orjson.loads(await f.read())
        generated = self.generate_bullshit(topic, length, data)
        generated_length = len(generated)
        resp = I18n.get(
            "fun.bullshit_generated", ctx.locale or ctx.guild_locale, [topic, generated_length]
        )
        if generated_length > 4096:
            file = discord.File(StringIO(generated), filename="bs.txt")
            return await ctx.respond(resp, file=file)
        embed = discord.Embed(title=resp, description=generated, color=discord.Color.blurple())
        return await ctx.respond(embed=embed)


def setup(bot: discord.AutoShardedBot) -> None:
    """
    The setup function for the cog.

    :param bot: The bot instance.
    :type bot: discord.AutoShardedBot
    """
    bot.add_cog(Fun(bot))
