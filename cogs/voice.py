import asyncio
import time

import discord
import youtube_dl
from discord.ext import commands
from lib import autocomplete, timer, chance
import gtts
import random
import os

#####################
#       voice       #
#####################
# All voice functions

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.vc_log = []

    # Save info on join/leave
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        await self.update_vc_log(member, before, after)

    #######################
    #       COMMANDS      #
    #######################

    # Send who just joined or left the vc
    @commands.slash_command(guild_ids = [730196305124655176])
    async def whojust(self, ctx):
        """Find out who recently joined or left the voice channel."""
        if len(self.vc_log) == 0:
            await ctx.respond("Nobody's done anything recently, bozo! 🤡", ephemeral=True)
            return

        msg = "Here's the scoop:"
        for data in self.vc_log:
            timestr = timer.get_timestr(int(time.time() - data["time"]))
            msg += f"\n{data['member']} {data['action']} {data['channel']} {timestr} ago."
        await ctx.respond(msg, ephemeral=True)

def setup(bot):
    bot.add_cog(Voice(bot))
