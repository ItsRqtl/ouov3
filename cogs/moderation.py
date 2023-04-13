from datetime import datetime, timedelta
from enum import Enum
from typing import Union

import discord.ui
from discord import (
    AutoShardedBot,
    Embed,
    InputTextStyle,
    Interaction,
    Member,
    SlashCommandOptionType,
    User,
    default_permissions,
    option,
)
from discord.ui import InputText, Modal

from utils.logging import Cog


class ReasonModalActionType(Enum):
    BAN = "封鎖"
    KICK = "踢出"


class ReasonModal(Modal):
    def __init__(self, user: Union[Member, User], action_type: ReasonModalActionType):
        self.user = user
        self.action_type = action_type

        super().__init__(InputText(label="動作原因", style=InputTextStyle.long), title="管理操作")

    async def callback(self, interaction: Interaction):
        if self.action_type == ReasonModalActionType.BAN:
            await interaction.guild.ban(self.user, reason=self.children[0].value)

        if self.action_type == ReasonModalActionType.KICK:
            await interaction.guild.kick(self.user, reason=self.children[0].value)

        await interaction.response.send_message(
            f"✅ 成功{self.action_type.value} {self.user.__str__()}", ephemeral=True
        )


class TimeoutModal(Modal):
    def __init__(self, user: Member):
        self.user = user

        super().__init__(
            InputText(label="動作原因", style=InputTextStyle.long),
            InputText(
                label="時間 (秒)",
                style=InputTextStyle.short,
                placeholder="60 - 一分鐘 | 3600 - 一小時 | 86400 - 一天 | 604800 - 一週",
            ),
            title="管理操作",
        )

    async def callback(self, interaction: Interaction):
        until_time = datetime.utcnow() + timedelta(seconds=int(self.children[1].value))

        await self.user.timeout(until_time, reason=self.children[0].value)

        await interaction.response.send_message(
            f"✅ 成功禁言 {self.user.__str__()} {int(self.children[1].value)} 秒", ephemeral=True
        )


class ModerationView(discord.ui.View):
    def __init__(self, user: Union[Member, User]):
        self.user = user

        super().__init__(timeout=180)

    @discord.ui.button(label="封鎖", style=discord.ButtonStyle.red)
    async def ban(self, button: discord.ui.Button, interaction: Interaction):
        await interaction.response.send_modal(ReasonModal(self.user, ReasonModalActionType.BAN))

    @discord.ui.button(label="踢出", style=discord.ButtonStyle.red)
    async def kick(self, button: discord.ui.Button, interaction: Interaction):
        if not interaction.guild.get_member(self.user.id):
            await interaction.response.send_message("❌ 不能對非伺服器成員進行踢出操作", ephemeral=True)

            return

        await interaction.response.send_modal(ReasonModal(self.user, ReasonModalActionType.KICK))

    @discord.ui.button(label="禁言", style=discord.ButtonStyle.red)
    async def mute(self, button: discord.ui.Button, interaction: Interaction):
        if not interaction.guild.get_member(self.user.id):
            await interaction.response.send_message("❌ 不能對非伺服器成員進行禁言操作", ephemeral=True)

            return

        await interaction.response.send_modal(TimeoutModal(self.user))


class Moderation(Cog):
    def __init__(self, bot: AutoShardedBot):
        self.bot = bot

    @discord.slash_command(name="mod", description="對成員的管理操作")
    @default_permissions(administrator=True)
    @option(
        input_type=SlashCommandOptionType.user,
        name="user",
        description="要進行管理操作的目標，與 user_id 互斥",
        required=False,
    )
    @option(
        input_type=SlashCommandOptionType.string,
        name="user_id",
        description="要進行管理操作的目標，與 user 互斥",
        required=False,
    )
    async def mod(
        self, interaction: Interaction, user: Union[User, Member] = None, user_id: str = None
    ):
        if user is None and user_id is None:
            await interaction.response.send_message("❌ 請提供 user 或 user_id")

            return

        if user is not None and user_id is not None:
            await interaction.response.send_message("❌ user 和 user_id 不能同時存在")

            return

        if not bool(user):
            user = interaction.guild.get_member(int(user_id)) or self.bot.get_user(user_id)

        await interaction.response.send_message(
            embed=Embed(
                color=0x2B2D31, title="管理操作", description=f"請選擇要對 {user.__str__()} 進行的管理操作"
            ),
            view=ModerationView(user),
        )


def setup(bot: AutoShardedBot) -> None:
    """
    The setup function for the cog.

    :param bot: The bot instance.
    :type bot: AutoShardedBot
    """
    bot.add_cog(Moderation(bot))
