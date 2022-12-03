import imp
import discord
from discord.ext import commands

from src.dababy_bot import DaBabyBot

#####################
#       stats       #
#####################
# Tracks member/server statistics
# Uses database to store/load

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot: DaBabyBot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        self.bot.db.add_to_field("members", str(message.author.id), "messageCount", 1)

def setup(bot):
    bot.add_cog(Stats(bot))