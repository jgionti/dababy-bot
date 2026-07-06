import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

from src import autocomplete, converterplus
from src.constants import GUILD_IDS
from src.dababy_bot import DaBabyBot

#####################
#       stats       #
#####################
# Tracks member/server statistics
# Uses database to store/load

class Stats(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: DaBabyBot = bot

    def ensure_member_exists(self, id: str):
        if self.bot.db.read("members", id) is None:
            self.bot.db.write("members", id, {})

    @commands.Cog.listener()
    async def on_ready(self):
        """On boot, ensure that all server members are added to the database."""
        for id in GUILD_IDS:
            guild = self.bot.get_guild(id)
            for member in guild.members:
                self.ensure_member_exists(str(member.id))

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """When a member joins, add them to the database."""
        self.ensure_member_exists(str(member.id))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        id = str(message.author.id)
        self.bot.db.add_to_field("members", id, "messageCount", 1)

    @app_commands.command()
    @app_commands.guilds(*GUILD_IDS)
    @app_commands.describe(
        member="Server member to get info about"
    )
    @app_commands.autocomplete(member=autocomplete.get_members)
    async def info(self, interaction: discord.Interaction, 
        member: Optional[str] = "me"
    ):
        """Displays info about a server member. Leave blank or type \"me\" to test yourself."""
        mem: discord.Member = await converterplus.lookup_member(interaction, member)
        members = self.bot.db.read_many("members")

        msg_count = 0
        total_msg_count = 0
        for m in members:
            total_msg_count += m.get("messageCount", 0)
            if m.get("_id") == str(mem.id):
                msg_count = m.get("messageCount", 0)

        msg_density = msg_count/total_msg_count
        role_str = await self.get_role_string(mem)
        embed = discord.Embed(color=mem.top_role.color, title=mem.name)
        embed.set_image(url=mem.display_avatar.with_size(128))
        embed.add_field(name="Mention", value=mem.mention)
        embed.add_field(name="Total Messages", value=(msg_count))
        embed.add_field(name="Message Density", value=(str(round(msg_density*100, 2))+"%"))
        embed.add_field(name="Roles", value=role_str, inline=False)
        embed.set_footer(text=f"Total Messages are counted since December 3rd, 2022. Serverwide count: {total_msg_count}")
        await interaction.response.send_message(content="", embed=embed)

async def setup(bot):
    await bot.add_cog(Stats(bot))