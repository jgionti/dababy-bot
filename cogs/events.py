import asyncio
import discord
from discord.ext import commands

#####################
#      events       #
#####################
# Commands and frameworks for starting/maintaining server events
# Mostly admin only commands

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Mr. Ping Challenge
        self.has_ping_challenge = False
        self.ping_map = {}
        self.ping_winner = None
        

    #######################
    #  HELPER FUNCTIONS   #
    #######################

    # Listener for user messages
    @commands.Cog.listener()
    async def on_message(self, message):
        # Mr. Ping Challenge
        if self.has_ping_challenge:
            # If author uses @everyone,
            if message.mention_everyone:
                # Add 1 to their count
                if message.author.id in self.ping_map:
                    self.ping_map[message.author.id] += 1
                else: self.ping_map[message.author.id] = 1
                # Win condition check
                if self.ping_map[message.author.id] == 19:
                    self.ping_winner = message.author
            # If author doesn't @everyone, streak was broken
            elif message.author.id in self.ping_map:
                self.ping_map[message.author.id] = 0


    #######################
    #       COMMANDS      #
    #######################

    # Main event command
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def event(self, ctx, name: str):
        if name in ["mrpingchallenge", "mpc"]:
            await self.mrpingchallenge(ctx)
        else:
            await ctx.message.add_reaction("\N{CROSS MARK}")


    # Mr Ping Challenge
    # The first user to ping @everyone 19 times in a row wins.
    async def mrpingchallenge(self, ctx):
        # Initialize challenge
        self.ping_map = {}
        self.ping_winner = None
        msg = "The Mr. Ping Challenge has started! The first user to complete it gets a prize!"
        await ctx.send(content=msg, file=discord.File("resources/MrPingChallenge.png"))
        self.has_ping_challenge = True

        # Loop while waiting for winner (a user has 19 pings)
        while self.ping_winner == None:
            await asyncio.sleep(1)

        # Print winner and send them to Brazil
        self.has_ping_challenge = False
        await ctx.send("Congratulations, " + self.ping_winner.mention + "! You've won the Mr. Ping Challenge! Now for your prize...")
        await asyncio.sleep(5)
        await self.bot.get_cog("Roles").brazil(ctx, str(self.ping_winner.id), time=600, reason="You pinged everyone 19 times!")



def setup(bot):
    bot.add_cog(Events(bot))