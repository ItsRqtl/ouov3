"""
Provide logging functionality for the bot.

This file is part of ouoteam/ouov3 which is released under GNU General Public License v3.0.
See file LISENCE for full license details.
"""

import os

os.environ["LOGURU_FORMAT"] = " | ".join(
    [
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>",
        "<level>{level: <8}</level>",
        "<level>{message}</level>",
    ]
)

import sys

from loguru._logger import Core, Logger


class Logging:
    """
    The Loguru library provides loggers to deal with logging in Python.
    This class provides a pre-instanced (and configured) logger for the bot.
    * Stop using print() and use this instead smh.

    :cvar __logger: The logger instance.
    :vartype __logger: loguru._logger.Logger
    """

    __logger = Logger(
        core=Core(),
        exception=None,
        depth=0,
        record=False,
        lazy=False,
        colors=False,
        raw=False,
        capture=True,
        patchers=[],
        extra={},
    )
    __logger.add(sys.stderr, level="DEBUG", diagnose=False, enqueue=True)
    __logger.add(
        "./logs/{time:YYYY-MM-DD_HH-mm-ss_SSS}.log",
        rotation="00:00",
        retention="30 days",
        encoding="utf-8",
        compression="gz",
        diagnose=False,
        level="INFO",
        enqueue=True,
    )

    @classmethod
    def get_logger(cls) -> Logger:
        """
        The logger instance.

        :return: The logger instance.
        :rtype: loguru._logger.Logger
        """
        return cls.__logger


from discord.ext import commands


class Cog(commands.Cog):
    """
    A custom Cog class that provides a pre-instanced logger.
    This class is inherited from commands.Cog and adds a logger instance.
    * Use this instead of commands.Cog
    """

    logger = Logging.get_logger()
