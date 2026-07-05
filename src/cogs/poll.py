from typing import List, Optional

import discord
from discord import app_commands
from discord.ext import commands

from src.constants import GUILD_IDS

#####################
#        poll       #
#####################
# Generate polls in a single command
# No timing or checking is done right now

class Poll(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _create_poll_embed(self, author: discord.Member, q: str, ops: List[str], reactions: List[str]) -> discord.Embed:
        desc = f"{q}\n\n"
        for i in range(0, len(ops)):
            desc += f"{reactions[i]} {ops[i]}\n"
        embed = discord.Embed(color=author.top_role.color, title=f"{author.display_name} calls a poll!", description=desc)
        embed.set_thumbnail(url = author.avatar.url)
        return embed

    # Use reactions to host a poll; currently untimed
    @app_commands.command()
    @app_commands.guilds(*GUILD_IDS)
    @app_commands.describe(
        question="Question to ask",
        op1="Option 1",
        op2="Option 2",
        op3="Option 3",
        op4="Option 4",
        op5="Option 5",
        op6="Option 6",
        op7="Option 7",
        op8="Option 8"
    )
    async def poll(self, interaction: discord.Interaction,
        question: str,
        op1: Optional[str],
        op2: Optional[str],
        op3: Optional[str],
        op4: Optional[str],
        op5: Optional[str],
        op6: Optional[str],
        op7: Optional[str],
        op8: Optional[str]
    ):
        """Ask the group a question and get feedback. Requires 2+ options."""
        args = [op1, op2, op3, op4, op5, op6, op7, op8]
        ops = []
        for op in args:
            if (op is not None):
                ops.append(op)

        reactions = []
        if len(ops) == 0:
            ops = ["Yes", "No"]
            reactions = ["✅", "❌"]
        elif len(ops) >= 2:
            reactions = ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭"]
        else:
            await interaction.response.send_message("👎 Poll must have at least 2 options!", ephemeral=True)
            return

        embed = self._create_poll_embed(interaction.user, question, ops, reactions)
        callback = await interaction.response.send_message(embed=embed)
        msg: discord.Message = callback.resource
        for i in range(0, len(ops)):
            await msg.add_reaction(reactions[i])
    

async def setup(bot: commands.Bot):
    await bot.add_cog(Poll(bot))
