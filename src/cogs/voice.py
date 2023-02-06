import time

import discord
from discord.ext import commands
from src import timer
from src.constants import GUILD_IDS

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
    #  HELPER FUNCTIONS   #
    #######################

    # Update VoiceState changelog for /vclog
    async def update_vc_log(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        action = ""
        channel = None

        # Return if a member is a bot
        if member.bot:
            return

        # Check for join
        if after.channel and (not before.channel or before.channel.id != after.channel.id):
            action = "joined"
            channel = after.channel
        # Check for leave
        elif before.channel and (not after.channel or after.channel.id != before.channel.id):
            action = "left"
            channel = before.channel

        # If a check passed, add to log
        if action != "":
            log_data = {"member" : member.mention, "action" : action, "channel" : channel.mention, "time" : time.time()}
            self.vc_log.insert(0, log_data)
            if (len(self.vc_log) > 10): self.vc_log.pop()

    #######################
    #       COMMANDS      #
    #######################

    # Send who just joined or left the vc
    @commands.slash_command(guild_ids = GUILD_IDS)
    async def vclog(self, ctx: discord.ApplicationContext):
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
