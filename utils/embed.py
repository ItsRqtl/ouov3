"""
Embed generating module.

This file is part of ouoteam/ouov3 which is released under GNU General Public License v3.0.
See file LISENCE for full license details.
"""

import random
from typing import Union

import discord


class Embed:
    """
    Generate embeds for the bot.
    """

    def error(error: str, color: Union[int, discord.Color] = 0xE74C3C) -> discord.Embed:
        """
        Generate an error embed.

        :param error: The error message.
        :type error: str

        :return: The generated embed.
        :rtype: discord.Embed
        """
        return discord.Embed(
            description=f":x: {error}",
            color=color,
        )

    def invisible() -> discord.Color:
        """
        Generate the Discord gray color.

        :return: The generated color.
        :rtype: discord.Color
        """
        return discord.Color(0x2B2D31)

    def random_color() -> discord.Color:
        """
        Generate a random color.
        Better implementation of discord.Color.random().

        :return: The generated color.
        :rtype: discord.Color
        """
        return discord.Color(random.randint(0, 0xFFFFFF))
