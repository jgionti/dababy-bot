import datetime
import discord
from discord.ext import commands
from cogs import timer

#####################
#       debug       #
#####################
# Commands for debugging and other niche testing

class Debug(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.timer_enabled = False
        self.timer = timer.Timer()

    #######################
    #  HELPER FUNCTIONS   #
    #######################

    # Execute additional operations before executing command
    @commands.Cog.listener()
    async def on_command(self, ctx):
        if self.timer_enabled:
            self.timer.start()

    # Execute additional operations after executing command
    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        if self.timer_enabled and ctx.command.name != "timermode":
            self.timer.stop()
            await ctx.channel.send("That command took me " + str(round(self.timer.get_time(),4)) + " seconds!")


    #######################
    #       COMMANDS      #
    #######################

    # Enables timer mode; prints how long a command took after each execution
    @commands.command(aliases = ["timer"], hidden=True)
    @commands.has_permissions(administrator=True)
    async def timermode(self, ctx):
        self.timer_enabled = not self.timer_enabled
        if self.timer_enabled:
            msg = "Timer has been enabled!"
        else:
            msg = "Timer has been disabled!"
        await ctx.send(msg)


    # Displays text channels and the last message time, highlighting those sent later than some amount of days
    @commands.command(aliases = ["cc"], hidden=True)
    async def channelcheckup(self, ctx, days=14):
        embed = discord.Embed(color=ctx.me.color, title=("Text Channel List"))
        first = second = ""
        for channel in ctx.guild.text_channels:
            if channel.category != None and channel.category.name.lower() == "retired":
                continue
            perm = channel.permissions_for(ctx.me)
            if perm.read_message_history == True and perm.read_messages == True:
                lst = await channel.history(limit=1).flatten()
            msg = lst[0] if lst else None
            first += channel.mention + '\n'
            date = msg.created_at if msg is not None else channel.created_at
            line = date.strftime("%m/%d/%Y, %H:%M:%S")
            if datetime.datetime.utcnow() - date >= datetime.timedelta(days=days):
                line = "**" + line + "**"
            line += "\n" if msg is not None else "*\n"
            second += line
            
        embed.add_field(name="Name", value=first)
        embed.add_field(name="Last Message Sent", value=second)
        embed.set_footer(text="Bolded date means the most recent message was sent "+str(days)+"+ days ago.\n* means a recent message was not found.")
        await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(Debug(bot))