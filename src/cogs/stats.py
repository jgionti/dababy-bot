import imp
import discord
from discord.ext import commands

from src.dababy_bot import DaBabyBot
import src.constants as constants

#####################
#       stats       #
#####################
# Tracks member/server statistics
# Uses database to store/load

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot: DaBabyBot = bot

    def ensure_member_exists(self, id: str):
        if self.bot.db.read("members", id) is None:
            self.bot.db.write("members", id, {})

    @commands.Cog.listener()
    async def on_ready(self):
        """On boot, ensure that all server members are added to the database."""
        for id in constants.GUILD_IDS:
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

def setup(bot):
    bot.add_cog(Stats(bot))