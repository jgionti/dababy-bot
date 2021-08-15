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

        # Stolen Letter Event
        self.has_sl_event = False
        self.stolen_char = 'n'

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

        # Stolen Letter Event
        if self.has_sl_event:
            if self.stolen_char in message.content.lower() and message.author != message.guild.me:
                # Add reaction
                await message.add_reaction("\N{CROSS MARK}")
                # Delete message after 1 seconds
                await message.delete(delay=1)


    #######################
    #       COMMANDS      #
    #######################

    # Main event command
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def event(self, ctx, *, arg: str):
        # Remove name from event arguments
        name = arg.split()[0]
        if len(arg.split()) > 1:
            arg = str(arg.split(None, 1)[1])
        else: arg = None

        # Parse name
        if name in ["mrpingchallenge", "mpc"]:
            await self.mrpingchallenge(ctx)
        elif name in ["stolenletter", "sl"]:
            await self.stolenletter(ctx) if arg == None else await self.stolenletter(ctx, arg)
        else: await ctx.message.add_reaction("\N{CROSS MARK}")


    # Reset all current events
    @commands.command(aliases = ["se"], hidden=True)
    @commands.has_permissions(administrator=True)
    async def stopevents(self, ctx):
        self.__init__(self.bot)
        await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")


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
        while self.ping_winner == None and self.has_ping_challenge:
            await asyncio.sleep(1)

        # Return early if event was cancelled
        if not self.has_ping_challenge:
            return

        # Print winner and send them to Brazil
        self.has_ping_challenge = False
        await ctx.send("Congratulations, " + self.ping_winner.mention + "! You've won the Mr. Ping Challenge! Now for your prize...")
        await asyncio.sleep(5)
        await self.bot.get_cog("Roles").brazil(ctx, str(self.ping_winner.id), time=600, reason="You pinged everyone 19 times!")


    # Stolen Letter Event
    # Automatically deletes any messages (not bot's) that have a certain letter in it
    async def stolenletter(self, ctx, stolen_char: str = 'n'):
        # Toggle event if already done
        if self.has_sl_event:
            self.has_sl_event = False
            await ctx.send("Let's go! The letter \'" + self.stolen_char + "\' has been found again!")
            return

        # Initialize event
        if len(stolen_char) != 1:
            await ctx.message.add_reaction("\N{CROSS MARK}")
            return
        self.stolen_char = stolen_char.lower()

        # Filter message and send
        msg = "Okay, very funny guys. Who snatched the letter \'" + self.stolen_char + "\'? " + \
            "This is actually a quite bad jump from before! **(All messages with the exiled letter will be zapped)**"
        msg = msg.replace(self.stolen_char, '')
        msg = msg.replace(self.stolen_char.upper(), '')
        await ctx.send(content=msg, file=discord.File("resources/StolenLetter.png"))

        # Start event
        self.has_sl_event = True



def setup(bot):
    bot.add_cog(Events(bot))