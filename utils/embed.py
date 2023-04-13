"""
Embed generating module.

This file is part of ouoteam/ouov3 which is released under GNU General Public License v3.0.
See file LISENCE for full license details.
"""
from __future__ import annotations

import random

import discord

__all__ = ["Embed", "Color"]


class Embed:
    """
    Generate embeds for the bot.
    """

    def error(error: str, color: int | discord.Color | None = None) -> discord.Embed:
        """
        Generate an error embed.

        :param error: The error message.
        :type error: str
        :param color: The color of the embed.
        :type color: Optional[Union[int, discord.Color]]

        :return: The generated embed.
        :rtype: discord.Embed
        """
        return discord.Embed(description=f":x: {error}", color=color or discord.Color.red())


class Color:
    """
    Generate colors for the bot.
    """

    def invisible() -> discord.Color:
        """
        A factory method that returns a discord.Color with a value of 0x2B2D31.

        :return: The generated color.
        :rtype: discord.Color
        """
        return discord.Color(0x2B2D31)

    def random(seed: int | str | float | bytes | bytearray | None = None) -> discord.Color:
        """
        A factory method that returns a discord.Color with a random rgb value.

        :param seed: The seed to initialize the RNG with. If None is passed the default RNG is used.
        :type seed: Optional[Union[int, str, float, bytes, bytearray]]

        :return: The generated color.
        :rtype: discord.Color
        """
        rand = random if seed is None else random.Random(seed)
        return discord.Color(rand.randint(0, 0xFFFFFF))
