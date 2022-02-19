import asyncio
import discord
from discord.ext import commands
import re

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

        # Max is Online Event
        self.has_max_event = False
        self.max_channel = None
        self.max_member = None
        self.gif_str = ""

    #######################
    #  HELPER FUNCTIONS   #
    #######################

    # Listener for user messages
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
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
            if self.stolen_char in message.content.lower() and message.webhook_id == None:
                webhook: discord.Webhook = await message.channel.create_webhook(name=message.author.display_name)
                msg = re.sub(self.stolen_char, "", message.content, flags = re.I)
                await message.delete()
                await webhook.send(msg, username=message.author.display_name, avatar_url=message.author.avatar_url)
                await webhook.delete()

    # Listener for change in member info
    # Max is Online is DREADFULLY hard coded, will need refactor in future
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        # Max is Online event
        if self.has_max_event:
            # Get Max's info only
            if before.id == self.max_member.id:
                if before.guild.id == 730196305124655176:
                    if (before.status != discord.Status.online and after.status == discord.Status.online)\
                        or (before.status != discord.Status.offline and after.status == discord.Status.offline)\
                        or (before.status != discord.Status.idle and after.status == discord.Status.idle)\
                        or (before.status != discord.Status.dnd and after.status == discord.Status.dnd):
                        await self.post_status(after)

    # Update self.gif_str and post status of a member to #max
    async def post_status(self, member: discord.Member):
        if member.status == discord.Status.online:
            self.gif_str = "https://tenor.com/view/max-online-dmc-devil-may-cry-dante-gif-21772253"
        elif member.status == discord.Status.offline:
            self.gif_str = "https://tenor.com/view/dmc-devil-may-cry-nero-max-max-is-offline-gif-21779492"
        elif member.status == discord.Status.idle:
            self.gif_str = "https://cdn.discordapp.com/attachments/290272452427251723/912784098014142504/dmc-max-away.gif"
        elif member.status == discord.Status.dnd:
            self.gif_str = "https://cdn.discordapp.com/attachments/290272452427251723/912784109925982308/dmc-max-dnd.gif"
        await self.max_channel.send(self.gif_str)

    #######################
    #       COMMANDS      #
    #######################

    # Main event command
    @commands.slash_command(guild_ids = [730196305124655176])
    @discord.has_role("Admin")
    async def event(self, ctx,
        event: discord.Option(str, "Event to toggle.", required = False)
    ):
        """Start an event or stop all running events."""
        # Remove name from event arguments
        name = event.split()[0]
        if len(event.split()) > 1:
            arg = str(event.split(None, 1)[1])
        else: arg = None
        # Parse name
        if name in ["mrpingchallenge", "mpc"]:
            await self.mrpingchallenge(ctx)
        elif name in ["stolenletter", "sl"]:
            await self.stolenletter(ctx) if arg == None else await self.stolenletter(ctx, arg)
        elif name in ["maxisonline", "max"]:
            await self.maxisonline(ctx)
        elif name in ["stop", "clear"]:
            await self.stopevents(ctx)
        else: await ctx.respond("\N{CROSS MARK}", ephemeral = True)

    # Reset all current events
    async def stopevents(self, ctx):
        self.__init__(self.bot)
        await ctx.respond("\N{WHITE HEAVY CHECK MARK} Stopped events!", ephemeral = True)

    # Mr Ping Challenge
    # The first user to ping @everyone 19 times in a row wins.
    async def mrpingchallenge(self, ctx):
        # Initialize challenge
        self.ping_map = {}
        self.ping_winner = None
        msg = "The Mr. Ping Challenge has started! The first user to complete it gets a prize!"
        await ctx.respond(content=msg, file=discord.File("resources/MrPingChallenge.png"))
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
        # Toggle event if active
        if self.has_sl_event:
            self.has_sl_event = False
            await ctx.respond("Let's go! The letter \'" + self.stolen_char + "\' has been found again!")
            return

        # Initialize event
        if len(stolen_char) != 1:
            await ctx.respond("\N{CROSS MARK} Only 1 character allowed!", ephemeral = True)
            return
        self.stolen_char = stolen_char.lower()

        # Filter message and send
        msg = "Okay, very funny guys. Who snatched the letter \'" + self.stolen_char + "\'? " + \
            "This is actually a quite bad jump from before! **(All messages with the exiled letter will be zapped)**"
        msg = msg.replace(self.stolen_char, '')
        msg = msg.replace(self.stolen_char.upper(), '')
        await ctx.respond(content=msg, file=discord.File("resources/StolenLetter.PNG"))

        # Start event
        self.has_sl_event = True

    # Max is Online Event
    # Sends the appropriate gif every time Cyanide#7815 changes status
    async def maxisonline(self, ctx):
        # Toggle event if active
        if self.has_max_event:
            self.has_max_event = False
            await self.max_channel.delete()
            self.max_channel = None
            self.max_member = None
            await ctx.respond("\N{SEE-NO-EVIL MONKEY}")
            return
        # Create new #max channel if one doesn't already exist
        try:
            self.max_channel: discord.TextChannel = await self.bot.get_cog("ConverterPlus").lookup_textchannel(ctx, "max")
        except commands.ChannelNotFound:
            self.max_channel: discord.TextChannel = await ctx.guild.create_text_channel("max", topic="max")
        # Create Max member objects
        max_id = 143524110813757440
        self.max_member: discord.Member = ctx.guild.get_member(max_id)
        if self.max_member.status == None:
            self.max_member.status = self.max_member.desktop_status
        # Start event and post current status
        await self.post_status(self.max_member)
        # Send starting reaction
        await ctx.respond("\N{EYES}")
        self.has_max_event = True

def setup(bot):
    bot.add_cog(Events(bot))