"""
The cog module for the Translate commands.

This file is part of ouoteam/ouov3 which is released under GNU General Public License v3.0.
See file LISENCE for full license details.
"""

from typing import Any, List

import aiohttp
import decouple
import discord
from discord.ext import commands

from utils.embed import Color, Embed
from utils.i18n import I18n


class Translate(commands.Cog):
    """
    Translation commands.

    :param bot: The bot instance.
    :type bot: discord.AutoShardedBot
    """

    target_lang = {
        "Bulgarian": "BG",
        "Czech": "CS",
        "Danish": "DA",
        "German": "DE",
        "Greek": "EL",
        "English": "EN",
        "Spanish": "ES",
        "Estonian": "ET",
        "Finnish": "FI",
        "French": "FR",
        "Hungarian": "HU",
        "Indonesian": "ID",
        "Italian": "IT",
        "Japanese": "JA",
        "Lithuanian": "LT",
        "Latvian": "LV",
        "Dutch": "NL",
        "Polish": "PL",
        "Portuguese": "PT",
        "Romanian": "RO",
        "Russian": "RU",
        "Slovak": "SK",
        "Slovenian": "SL",
        "Swedish": "SV",
        "Turkish": "TR",
        "Ukrainian": "UK",
        "Chinese (simplified)": "ZH",
    }

    original_lang = {
        "Bulgarian": "BG",
        "Czech": "CS",
        "Danish": "DA",
        "German": "DE",
        "Greek": "EL",
        "English": "EN",
        "Spanish": "ES",
        "Estonian": "ET",
        "Finnish": "FI",
        "French": "FR",
        "Hungarian": "HU",
        "Indonesian": "ID",
        "Italian": "IT",
        "Japanese": "JA",
        "Lithuanian": "LT",
        "Latvian": "LV",
        "Dutch": "NL",
        "Polish": "PL",
        "Portuguese": "PT",
        "Romanian": "RO",
        "Russian": "RU",
        "Slovak": "SK",
        "Slovenian": "SL",
        "Swedish": "SV",
        "Turkish": "TR",
        "Ukrainian": "UK",
        "Chinese": "ZH",
    }

    def __init__(self, bot: discord.AutoShardedBot) -> None:
        self.bot = bot

    async def _target_autocomplete(
        self, ctx: discord.AutocompleteContext
    ) -> List[discord.OptionChoice]:
        """
        Autocomplete for the target language option.

        :param ctx: The context of the autocomplete.
        :type ctx: discord.AutocompleteContext

        :return: The list of choices.
        :rtype: List[discord.OptionChoice]
        """
        target = ctx.options["target"] or ""
        langs = list(self.target_lang.keys())
        if not (letters := list(target) if target != "" else []):
            return [
                discord.OptionChoice(name=i, value=self.target_lang[i])
                for i in (langs[:24] if len(langs) > 25 else langs)
            ]
        choices: list = []
        focus: str = "".join(letters)
        for i in langs:
            if focus.lower() in i.lower() and len(choices) < 26:
                choices.append(discord.OptionChoice(name=i, value=self.target_lang[i]))
            elif len(choices) >= 26:
                break
        return choices

    async def _original_autocomplete(
        self, ctx: discord.AutocompleteContext
    ) -> List[discord.OptionChoice]:
        """
        Autocomplete for the original language option.

        :param ctx: The context of the autocomplete.
        :type ctx: discord.AutocompleteContext

        :return: The list of choices.
        :rtype: List[discord.OptionChoice]
        """
        target = ctx.options["original"] or ""
        langs = list(self.original_lang.keys())
        if not (letters := list(target) if target != "" else []):
            return [
                discord.OptionChoice(name=i, value=self.original_lang[i])
                for i in (langs[:24] if len(langs) > 25 else langs)
            ]
        choices: list = []
        focus: str = "".join(letters)
        for i in langs:
            if focus.lower() in i.lower() and len(choices) < 26:
                choices.append(discord.OptionChoice(name=i, value=self.original_lang[i]))
            elif len(choices) >= 26:
                break
        return choices

    async def _translate(self, text: str, target: str, source: str = "") -> Any:
        """
        Perform a translation using DeepL.
        This is an internal function used by the translate command.

        :param text: The text to translate.
        :type text: str
        :param target: The target language.
        :type target: str
        :param source: The source language, defaults to auto.
        :type source: str

        :return: The result of the translation api call.
        :rtype: Any
        """
        async with aiohttp.ClientSession() as s, s.post(
            "https://api-free.deepl.com/v2/translate",
            headers={"Authorization": f"DeepL-Auth-Key {decouple.config('deepl_api_key')}"},
            data={"text": text, "target_lang": target, "source_lang": source},
        ) as r:
            if r.status not in [429, 456]:
                if "translations" not in (j := await r.json()):
                    return r.status, None
                return (
                    j["translations"][0]["text"],
                    j["translations"][0]["detected_source_language"],
                )
            return r.status, None

    @discord.slash_command(
        name="translate",
        description="Translate a text.",
        description_localizations={
            "zh-TW": "翻譯一段文字",
            "zh-CN": "翻译一段文字",
        },
    )
    @discord.option(
        name="text",
        description="The text to translate.",
        description_localizations={
            "zh-TW": "要翻譯的文字",
            "zh-CN": "要翻译的文字",
        },
        max_length=128,
    )
    @discord.option(
        name="target",
        description="The target language.",
        description_localizations={
            "zh-TW": "目標語言",
            "zh-CN": "目标语言",
        },
        autocomplete=_target_autocomplete,
    )
    @discord.option(
        name="original",
        description="The original language (leave blank for auto-detect).",
        description_localizations={
            "zh-TW": "原始語言 (留空為自動偵測)",
            "zh-CN": "原始语言 (留空为自动检测)",
        },
        autocomplete=_original_autocomplete,
    )
    async def translate(
        self, ctx: discord.ApplicationContext, text: str, target: str, original: str = ""
    ) -> discord.Message:
        """
        Translate a text.

        :param ctx: The context of the command.
        :type ctx: discord.ApplicationContext
        :param text: The text to translate.
        :type text: str
        :param target: The target language.
        :type target: str
        :param original: The original language (leave blank for auto-detect).
        :type original: str

        :return: The message sent.
        :rtype: discord.Message
        """
        await ctx.defer()
        resp, lang = await self._translate(text, target, original)
        if resp == 429:
            return await ctx.respond(
                embed=Embed.error(
                    I18n.get("translate.translate.ratelimited", ctx.locale or ctx.guild_locale)
                )
            )
        if resp == 456:
            return await ctx.respond(
                embed=Embed.error(
                    I18n.get("translate.translate.out_of_quota", ctx.locale or ctx.guild_locale)
                )
            )
        embed = discord.Embed(
            title=I18n.get("translate.translate.result.title", ctx.locale or ctx.guild_locale),
            description=I18n.get(
                "translate.translate.result.description",
                ctx.locale or ctx.guild_locale,
                url=f"https://www.deepl.com/translator#{lang}/{target}/{text}",
            )
            if len(resp) > 1024
            else "",
            color=Color.random(),
        )
        embed.add_field(
            name=I18n.get("translate.translate.result.original", ctx.locale or ctx.guild_locale),
            value=text,
            inline=False,
        )
        embed.add_field(
            name=I18n.get("translate.translate.result.translated", ctx.locale or ctx.guild_locale),
            value=resp if len(resp) <= 1024 else f"{resp[:1020]}...",
            inline=False,
        )
        embed.set_footer(
            text=I18n.get(
                "translate.translate.result.footer",
                ctx.locale or ctx.guild_locale,
                original_lang=(
                    [k for k, v in self.original_lang.items() if v == lang][0]
                    if self.original_lang != ""
                    else I18n.get("translate.translate.result.original_auto")
                ),
                target_lang=([k for k, v in self.target_lang.items() if v == target][0]),
            ),  # text="DeepL 翻譯 {original_lang} → {target_lang}",
        )
        return await ctx.respond(embed=embed)


def setup(bot: discord.AutoShardedBot) -> None:
    """
    The setup function for the cog.

    :param bot: The bot instance.
    :type bot: discord.AutoShardedBot
    """
    bot.add_cog(Translate(bot))
