"""
The cog module for the calculator.

This file is part of ouoteam/ouov3 which is released under GNU General Public License v3.0.
See file LISENCE for full license details.
"""
from __future__ import annotations

import operator

import discord

from utils.i18n import I18n
from utils.logging import Cog


class CalculatorView(discord.ui.View):
    """
    The calculator view.
    """

    ops = {"+": operator.add, "-": operator.sub, "×": operator.mul, "÷": operator.truediv}

    def __init__(self, author_id: int, bot: discord.AutoShardedBot):
        super().__init__()
        self.author_id = author_id
        self.bot = bot
        self.result = self.last_number = "0"
        self.last_operation = None
        self.clear_next = False

    def get_locale(self, interaction: discord.Interaction) -> str | None:
        """
        Get the locale of the interaction.

        :param interaction: The interaction.
        :type interaction: discord.Interaction

        :return: The locale or None if not found.
        :rtype: str | None
        """
        return interaction.locale or interaction.guild_locale

    async def edit_skip(self, interaction: discord.Interaction) -> discord.Message:
        """
        Edit the message without changing the embed.

        :param interaction: The interaction.
        :type interaction: discord.Interaction

        :return: The edited message.
        :rtype: discord.Message
        """
        return await interaction.response.edit_message()

    async def edit_embed(self, interaction: discord.Interaction) -> discord.Message:
        """
        Edit the message with the embed.

        :param interaction: The interaction.
        :type interaction: discord.Interaction

        :return: The edited message.
        :rtype: discord.Message
        """
        embed = discord.Embed(
            description=f"```{self.result.rjust(30)}```", color=discord.Color.blurple()
        )
        return await interaction.response.edit_message(embed=embed)

    async def handle_number(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> discord.Message:
        """
        Handle the number button.

        :param button: The button.
        :type button: discord.ui.Button
        :param interaction: The interaction.
        :type interaction: discord.Interaction

        :return: The edited message.
        :rtype: discord.Message
        """
        number = button.label
        if self.clear_next or self.result == "0":
            self.clear_next = False
            self.result = number
        else:
            self.result += number
        return await self.edit_embed(interaction)

    async def handle_operation(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> discord.Message:
        """
        Handle the operation button.

        :param button: The button.
        :type button: discord.ui.Button
        :param interaction: The interaction.
        :type interaction: discord.Interaction

        :return: The edited message.
        :rtype: discord.Message
        """
        if self.last_operation is not None:
            op_func = self.ops[self.last_operation]
            result = op_func(float(self.last_number), float(self.result))
            self.last_number = str(round(result, 10)).rstrip("0").rstrip(".")
        else:
            self.last_number = self.result
        self.last_operation = button.label
        self.result = "0"
        return await self.edit_embed(interaction)

    @discord.ui.button(label="AC", style=discord.ButtonStyle.danger)
    async def all_clear(
        self, _: discord.ui.Button, interaction: discord.Interaction
    ) -> discord.Message:
        """
        Handle the all clear button.

        :param button: The button.
        :type button: discord.ui.Button
        :param interaction: The interaction.
        :type interaction: discord.Interaction

        :return: The edited message.
        :rtype: discord.Message
        """
        self.result = "0"
        self.last_number = 0
        self.last_operation = None
        return await self.edit_embed(interaction)

    @discord.ui.button(label="C", style=discord.ButtonStyle.danger)
    async def clear(
        self, _: discord.ui.Button, interaction: discord.Interaction
    ) -> discord.Message:
        """
        Handle the clear button.

        :param button: The button.
        :type button: discord.ui.Button
        :param interaction: The interaction.
        :type interaction: discord.Interaction

        :return: The edited message.
        :rtype: discord.Message
        """
        self.result = "0"
        return await self.edit_embed(interaction)

    @discord.ui.button(label="←", style=discord.ButtonStyle.primary)
    async def backspace(
        self, _: discord.ui.Button, interaction: discord.Interaction
    ) -> discord.Message:
        """
        Handle the backspace button.

        :param button: The button.
        :type button: discord.ui.Button
        :param interaction: The interaction.
        :type interaction: discord.Interaction

        :return: The edited message.
        :rtype: discord.Message
        """
        if self.result == "0":
            return await self.edit_skip(interaction)
        self.result = self.result[:-1]
        if self.clear_next or self.result == "":
            self.result = "0"
        return await self.edit_embed(interaction)

    @discord.ui.button(label="÷", style=discord.ButtonStyle.secondary)
    async def divide(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> discord.Message:
        """
        Handle the divide button.

        :param button: The button.
        :type button: discord.ui.Button
        :param interaction: The interaction.
        :type interaction: discord.Interaction

        :return: The edited message.
        :rtype: discord.Message
        """
        return await self.handle_operation(button, interaction)

    @discord.ui.button(label="1", style=discord.ButtonStyle.success, row=1)
    async def one(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> discord.Message:
        """
        Handle the one button.

        :param button: The button.
        :type button: discord.ui.Button
        :param interaction: The interaction.
        :type interaction: discord.Interaction

        :return: The edited message.
        :rtype: discord.Message
        """
        return await self.handle_number(button, interaction)

    @discord.ui.button(label="2", style=discord.ButtonStyle.success, row=1)
    async def two(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> discord.Message:
        """
        Handle the two button.

        :param button: The button.
        :type button: discord.ui.Button
        :param interaction: The interaction.
        :type interaction: discord.Interaction

        :return: The edited message.
        :rtype: discord.Message
        """
        return await self.handle_number(button, interaction)

    @discord.ui.button(label="3", style=discord.ButtonStyle.success, row=1)
    async def three(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> discord.Message:
        """
        Handle the three button.

        :param button: The button.
        :type button: discord.ui.Button
        :param interaction: The interaction.
        :type interaction: discord.Interaction

        :return: The edited message.
        :rtype: discord.Message
        """
        return await self.handle_number(button, interaction)

    @discord.ui.button(label="×", style=discord.ButtonStyle.secondary, row=1)
    async def multiply(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> discord.Message:
        """
        Handle the multiply button.

        :param button: The button.
        :type button: discord.ui.Button
        :param interaction: The interaction.
        :type interaction: discord.Interaction

        :return: The edited message.
        :rtype: discord.Message
        """
        return await self.handle_operation(button, interaction)

    @discord.ui.button(label="4", style=discord.ButtonStyle.success, row=2)
    async def four(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> discord.Message:
        """
        Handle the four button.

        :param button: The button.
        :type button: discord.ui.Button
        :param interaction: The interaction.
        :type interaction: discord.Interaction

        :return: The edited message.
        :rtype: discord.Message
        """
        return await self.handle_number(button, interaction)

    @discord.ui.button(label="5", style=discord.ButtonStyle.success, row=2)
    async def five(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> discord.Message:
        """
        Handle the five button.

        :param button: The button.
        :type button: discord.ui.Button
        :param interaction: The interaction.
        :type interaction: discord.Interaction

        :return: The edited message.
        :rtype: discord.Message
        """
        return await self.handle_number(button, interaction)

    @discord.ui.button(label="6", style=discord.ButtonStyle.success, row=2)
    async def six(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> discord.Message:
        """
        Handle the six button.

        :param button: The button.
        :type button: discord.ui.Button
        :param interaction: The interaction.
        :type interaction: discord.Interaction

        :return: The edited message.
        :rtype: discord.Message
        """
        return await self.handle_number(button, interaction)

    @discord.ui.button(label="-", style=discord.ButtonStyle.secondary, row=2)
    async def subtract(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> discord.Message:
        """
        Handle the subtract button.

        :param button: The button.
        :type button: discord.ui.Button
        :param interaction: The interaction.
        :type interaction: discord.Interaction

        :return: The edited message.
        :rtype: discord.Message
        """
        return await self.handle_operation(button, interaction)

    @discord.ui.button(label="7", style=discord.ButtonStyle.success, row=3)
    async def seven(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> discord.Message:
        """
        Handle the seven button.

        :param button: The button.
        :type button: discord.ui.Button
        :param interaction: The interaction.
        :type interaction: discord.Interaction

        :return: The edited message.
        :rtype: discord.Message
        """
        return await self.handle_number(button, interaction)

    @discord.ui.button(label="8", style=discord.ButtonStyle.success, row=3)
    async def eight(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> discord.Message:
        """
        Handle the eight button.

        :param button: The button.
        :type button: discord.ui.Button
        :param interaction: The interaction.
        :type interaction: discord.Interaction

        :return: The edited message.
        :rtype: discord.Message
        """
        return await self.handle_number(button, interaction)

    @discord.ui.button(label="9", style=discord.ButtonStyle.success, row=3)
    async def nine(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> discord.Message:
        """
        Handle the nine button.

        :param button: The button.
        :type button: discord.ui.Button
        :param interaction: The interaction.
        :type interaction: discord.Interaction

        :return: The edited message.
        :rtype: discord.Message
        """
        return await self.handle_number(button, interaction)

    @discord.ui.button(label="+", style=discord.ButtonStyle.secondary, row=3)
    async def add(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> discord.Message:
        """
        Handle the add button.

        :param button: The button.
        :type button: discord.ui.Button
        :param interaction: The interaction.
        :type interaction: discord.Interaction

        :return: The edited message.
        :rtype: discord.Message
        """
        return await self.handle_operation(button, interaction)

    @discord.ui.button(label="+/-", style=discord.ButtonStyle.primary, row=3)
    async def negate(
        self, _: discord.ui.Button, interaction: discord.Interaction
    ) -> discord.Message:
        """
        Handle the negate button.

        :param button: The button.
        :type button: discord.ui.Button
        :param interaction: The interaction.
        :type interaction: discord.Interaction

        :return: The edited message.
        :rtype: discord.Message
        """
        if self.result == "0":
            return await self.edit_skip(interaction)
        if self.result.startswith("-"):
            self.result = self.result[1:]
        else:
            self.result = f"-{self.result}"
        if self.clear_next:
            self.clear_next = False
        return await self.edit_embed(interaction)

    @discord.ui.button(label="?", style=discord.ButtonStyle.primary, row=4)
    async def help(self, _: discord.ui.Button, interaction: discord.Interaction) -> discord.Message:
        """
        Handle the help button.

        :param button: The button.
        :type button: discord.ui.Button
        :param interaction: The interaction.
        :type interaction: discord.Interaction

        :return: The response message.
        :rtype: discord.Message
        """
        locale = self.get_locale(interaction)
        embed = discord.Embed(
            title=I18n.get("calculator.help.title", locale),
            description=I18n.get("calculator.help.description", locale),
            color=discord.Color.blurple(),
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="0", style=discord.ButtonStyle.success, row=4)
    async def zero(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> discord.Message:
        """
        Handle the zero button.

        :param button: The button.
        :type button: discord.ui.Button
        :param interaction: The interaction.
        :type interaction: discord.Interaction

        :return: The edited message.
        :rtype: discord.Message
        """
        return await self.handle_number(button, interaction)

    @discord.ui.button(label=".", style=discord.ButtonStyle.success, row=4)
    async def dot(self, _: discord.ui.Button, interaction: discord.Interaction) -> discord.Message:
        """
        Handle the dot button.

        :param button: The button.
        :type button: discord.ui.Button
        :param interaction: The interaction.
        :type interaction: discord.Interaction

        :return: The edited message.
        :rtype: discord.Message
        """
        if self.clear_next:
            self.result = "0."
            self.clear_next = False
        elif "." in self.result:
            return await self.edit_skip(interaction)
        else:
            self.result = f"{self.result}."
        return await self.edit_embed(interaction)

    @discord.ui.button(label="=", style=discord.ButtonStyle.secondary, row=4)
    async def equal(
        self, _: discord.ui.Button, interaction: discord.Interaction
    ) -> discord.Message:
        """
        Handle the equal button.

        :param button: The button.
        :type button: discord.ui.Button
        :param interaction: The interaction.
        :type interaction: discord.Interaction

        :return: The edited message.
        :rtype: discord.Message
        """
        if not self.last_operation:
            return await self.edit_skip(interaction)
        op_func = self.ops[self.last_operation]
        result = op_func(float(self.last_number), float(self.result))
        self.result = str(round(result, 10)).rstrip("0").rstrip(".")
        self.last_number = "0"
        self.last_operation = None
        self.clear_next = True
        return await self.edit_embed(interaction)

    @discord.ui.button(label="X", style=discord.ButtonStyle.danger, row=4)
    async def close(
        self, _: discord.ui.Button, interaction: discord.Interaction
    ) -> discord.Message:
        """
        Handle the close button.

        :param button: The button.
        :type button: discord.ui.Button
        :param interaction: The interaction.
        :type interaction: discord.Interaction

        :return: The edited message.
        :rtype: discord.Message
        """
        self.stop()
        return await interaction.response.edit_message(
            content=I18n.get("calculator.closed", self.get_locale(interaction)),
            embed=None,
            view=None,
            delete_after=3,
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """
        Check if the interaction is valid.

        :param interaction: The interaction.
        :type interaction: discord.Interaction

        :return: Whether the interaction is valid.
        :rtype: bool
        """
        return interaction.user.id == self.author_id

    async def on_check_failure(self, interaction: discord.Interaction) -> discord.Message:
        """
        Handle the check failure.

        :param interaction: The interaction.
        :type interaction: discord.Interaction

        :return: The response message.
        :rtype: discord.Message
        """
        return await interaction.response.send_message(
            I18n.get(
                "calculator.check_failed",
                self.get_locale(interaction),
                command_id=self.bot.get_command("calculator").id,
            ),
            ephemeral=True,
        )


class CalculatorCog(Cog):
    """
    The calculator cog.

    :param bot: The bot.
    :type bot: discord.AutoShardedBot
    """

    def __init__(self, bot: discord.AutoShardedBot) -> None:
        self.bot = bot

    @discord.slash_command(
        description="Open a calculator.",
        description_localizations={"zh-TW": "開啟一個計算機。", "zh-CN": "开启一个计算器。"},
    )
    async def calculator(self, ctx: discord.ApplicationContext) -> discord.Message:
        """
        Open a calculator.

        :param ctx: The context.
        :type ctx: discord.ApplicationContext

        :return: The response message.
        :rtype: discord.Message
        """
        await ctx.defer()
        msg = await ctx.respond(
            content=I18n.get("calculator.opening", ctx.locale or ctx.guild_locale)
        )
        embed = discord.Embed(description=f"```{'0'.rjust(30)}```", color=discord.Color.blurple())
        await msg.edit(content="", embed=embed, view=CalculatorView(ctx.author.id, self.bot))


def setup(bot: discord.AutoShardedBot) -> None:
    """
    The setup function for the cog.

    :param bot: The bot.
    :type bot: discord.AutoShardedBot
    """
    bot.add_cog(CalculatorCog(bot))
