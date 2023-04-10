"""
The cog module for event listeners to protect the server from bad things.

This file is part of ouoteam/ouov3 which is released under GNU General Public License v3.0.
See file LISENCE for full license details.
"""

import binascii
import contextlib
import datetime
import re
from base64 import b64decode
from enum import Enum
from typing import List

import aiohttp
import decouple
import discord
from discord.ext import commands

from utils.embed import Color
from utils.i18n import I18n


class ThreatType(Enum):
    """
    The threat type of a URL scan.
    """

    THREAT_TYPE_UNSPECIFIED = "protection.threadtype.THREAT_TYPE_UNSPECIFIED"
    MALWARE = "protection.threadtype.MALWARE"
    SOCIAL_ENGINEERING = "protection.threadtype.SOCIAL_ENGINEERING"
    UNWANTED_SOFTWARE = "protection.threadtype.UNWANTED_SOFTWARE"
    POTENTIALLY_HARMFUL_APPLICATION = "protection.threadtype.POTENTIALLY_HARMFUL_APPLICATION"


class PlatformType(Enum):
    """
    The platform type of a threat.
    """

    PLATFORM_TYPE_UNSPECIFIED = "protection.platformtype.PLATFORM_TYPE_UNSPECIFIED"
    WINDOWS = "protection.platformtype.WINDOWS"
    LINUX = "protection.platformtype.LINUX"
    ANDROID = "protection.platformtype.ANDROID"
    OSX = "protection.platformtype.OSX"
    IOS = "protection.platformtype.IOS"
    ANY_PLATFORM = "protection.platformtype.ANY_PLATFORM"
    ALL_PLATFORM = "protection.platformtype.ALL_PLATFORM"
    CHROME = "protection.platformtype.CHROME"


class Match:
    """
    A match object of a URL scan.
    """

    def __init__(self, data: dict):
        self.url = data["threat"]["url"]
        self.threat_type = ThreatType[data["threatType"]].value
        self.platform_type = PlatformType[data["platformType"]].value

    def get_message(self, locale: str) -> str:
        """
        Get the message of the match.

        :param locale: The locale of the message.
        :type locale: str

        :return: The message.
        :rtype: str
        """
        platform = I18n.get(self.platform_type, locale)
        threat = I18n.get(self.threat_type, locale)
        return I18n.get("protection.urlscan.match", locale, threat=threat, platform=platform)

    def get_matches(data: list) -> List["Match"]:
        """
        Get a list of matches from a list of data.

        :param data: The data to get matches from.
        :type data: list

        :return: A list of matches.
        :rtype: List[Match]
        """
        return [Match(match) for match in data]


class Protection(commands.Cog):
    """
    Protection event cog.

    :param bot: The bot instance.
    :type bot: discord.AutoShardedBot
    """

    url_regex = re.compile(
        r"(http|https)(:\/\/)([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])"
    )
    token_regex = re.compile(r"[a-zA-Z0-9_-]{23,28}\.[a-zA-Z0-9_-]{6,7}\.[a-zA-Z0-9_-]{27,}")

    def __init__(self, bot: discord.AutoShardedBot) -> None:
        self.bot = bot

    async def lookup_google_safebrowsing(self, links: list) -> dict:
        """
        Lookup a list of URLs in Google Safe Browsing.
        """
        async with aiohttp.ClientSession() as s, s.post(
            f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={decouple.config('google_api_key')}",
            headers={"Content-Type": "application/json"},
            data=str(
                {
                    "client": {"clientId": "OuO Bot", "clientVersion": self.bot.version},
                    "threatInfo": {
                        "threatTypes": [
                            "MALWARE",
                            "SOCIAL_ENGINEERING",
                            "UNWANTED_SOFTWARE",
                            "POTENTIALLY_HARMFUL_APPLICATION",
                        ],
                        "platformTypes": ["ANY_PLATFORM"],
                        "threatEntryTypes": ["URL"],
                        "threatEntries": [{"url": i} for i in links],
                    },
                }
            ),
        ) as r:
            return await r.json()

    # TEST URL: http://malware.testing.google.test/testing/malware/*
    @commands.Cog.listener("on_message")
    async def url_safecheck(self, message: discord.Message) -> None:
        """
        Scan all URLs in the message and check if they are safe.

        :param message: The message object.
        :type message: discord.Message
        """
        if (
            message.channel.type is discord.ChannelType.private
            or not message.guild
            or not message.content
            or not message.channel.permissions_for(message.guild.me).send_messages
        ):
            return
        if linklist := self.url_regex.findall(message.content):
            matches = (
                await self.lookup_google_safebrowsing([*{"".join(i) for i in linklist}])
            ).get("matches", None)
            if matches is None:
                return
            embeds = []
            now = datetime.datetime.now()
            title = I18n.get("protection.urlscan.title", message.guild.preferred_locale)
            description = I18n.get("protection.urlscan.description", message.guild.preferred_locale)
            footer = I18n.get("protection.urlscan.footer", message.guild.preferred_locale)
            for i in discord.utils.as_chunks(Match.get_matches(matches), 5):
                embed = discord.Embed(
                    title=title,
                    description=description,
                    fields=[
                        discord.EmbedField(
                            name=f"URL: ||<{match.url}>||",
                            value=match.get_message(message.guild.preferred_locale),
                            inline=False,
                        )
                        for match in i
                    ],
                    color=Color.invisible(),
                    timestamp=now,
                ).set_footer(text=footer)
                embeds.append(embed)
            if len(embeds) > 10:
                ...  # TODO: Seriously 50 unique harmful link results in a single message??
            else:
                await message.reply(embeds=embeds)

    @commands.Cog.listener("on_message")
    async def token_safecheck(self, message: discord.Message) -> None:
        """
        Scan all message to check for discord tokens.
        """
        if (
            message.channel.type is discord.ChannelType.private
            or not message.guild
            or not message.content
            or not message.channel.permissions_for(message.guild.me).send_messages
        ):
            return
        for token in list(self.token_regex.findall(message.content)):
            try:
                validate = b64decode(token.split(".")[0] + "==", validate=True)
            except binascii.Error:
                continue
            else:
                if validate.isdigit():
                    locale = message.guild.preferred_locale
                    try:
                        await message.delete()
                    except Exception:
                        await message.reply(
                            message.author.mention,
                            embed=discord.Embed(
                                title=I18n.get("protection.token.title", locale),
                                description=I18n.get(
                                    "protection.token.description.no_perms", locale
                                ),
                                color=Color.invisible(),
                            ),
                        )
                    else:
                        await message.channel.send(
                            message.author.mention,
                            embed=discord.Embed(
                                title=I18n.get("protection.token.title", locale),
                                description=I18n.get(
                                    "protection.token.description.deleted", locale
                                ),
                                color=Color.invisible(),
                            ),
                        )
                    finally:
                        break

    @commands.Cog.listener("on_message_delete")
    async def ghost_ping(self, message: discord.Message) -> None:
        """
        Detect ghost pings.
        """
        if (
            not message.author
            or message.author.id == self.bot.user.id
            or (not message.mentions and not message.mention_everyone and not message.role_mentions)
            or message.channel.type == discord.ChannelType.private
            or not message.guild
        ):
            return
        roles = []
        victims = []
        can_mention_all = message.channel.permissions_for(message.guild.me).mention_everyone
        everyone = bool(message.mention_everyone and can_mention_all)
        if message.role_mentions:
            roles.extend(
                f"<@&{i.id}>"
                for i in message.role_mentions
                if (i.mentionable or can_mention_all) and not i.managed
            )
        if message.mentions:
            victims.extend(
                f"<@{i.id}>" for i in message.mentions if not i.bot and i.id != message.author.id
            )
        if not victims and not roles and not everyone:
            return
        content = ""
        if everyone:
            content = "@everyone"
        else:
            content = ""
            if roles:
                content += I18n.get("protection.ghostping.role", message.guild.preferred_locale)
                content += "\n".join(roles)
            if victims:
                if content != "":
                    content += "\n\n"
                content += I18n.get("protection.ghostping.user", message.guild.preferred_locale)
                content += "\n".join(victims)
        with contextlib.suppress(Exception):
            await message.channel.send(
                embed=discord.Embed(
                    title=I18n.get("protection.ghostping.title", message.guild.preferred_locale),
                    description=I18n.get(
                        "protection.ghostping.description",
                        message.guild.preferred_locale,
                        author=message.author.mention,
                        content=content,
                    ),
                    color=Color.invisible(),
                )
            )


def setup(bot: discord.AutoShardedBot) -> None:
    """
    Add the cog to the bot.

    :param bot: The bot instance.
    :type bot: discord.AutoShardedBot
    """
    bot.add_cog(Protection(bot))
