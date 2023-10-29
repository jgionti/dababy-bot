import discord
from discord.ext import tasks
from src.events.event import Event
from src import converterplus

INTERVAL = 30.0


class MaxIsOnlineEvent(Event):
    """Event class for the Max is Online event.

    Every time Cyanide#7815 changes status, the bot sends a gif
    corresponding to his latest status into the #max thread.

    args:
        [0] - specific channel to do event in
        [1] - interval between status posts
    """

    def __init__(self, bot):
        super().__init__(bot, aliases=["maxisonline"])
        self.interval = INTERVAL
        self.max_thread = None
        self.max_member = None
        self.gif_str = ""

    @tasks.loop(minutes=INTERVAL)
    async def post(self):
        await self._post_status(self.max_member)

    # Update self.gif_str and post status of a member to #max
    async def _post_status(self, member: discord.Member):
        if member.is_on_mobile():
            self.gif_str = "https://tenor.com/view/devil-may-cry-max-mobile-phone-dante-gif-12410814099756203738"
        elif member.status == discord.Status.online:
            self.gif_str = "https://tenor.com/view/max-online-dmc-devil-may-cry-dante-gif-21772253"
        elif member.status == discord.Status.offline:
            self.gif_str = "https://tenor.com/view/dmc-devil-may-cry-nero-max-max-is-offline-gif-21779492"
        elif member.status == discord.Status.idle:
            self.gif_str = "https://tenor.com/view/devil-may-cry-max-max-is-away-away-vergil-gif-7447214506811831601"
        elif member.status == discord.Status.dnd:
            self.gif_str = "https://tenor.com/view/max-do-not-disturb-devil-may-cry-vergil-gif-6822476653861822416"
        await self.max_thread.send(self.gif_str)

    async def start(self, ctx, args):
        # Create new max thread in whichever channel is specified in the second arg if it doesn't already exist
        self.interval = INTERVAL
        channel_name = "general"

        if (len(args) == 1):
            # CASE 1: 1 argument, interval only
            try:
                self.interval = float(args[0])
            # CASE 2: 1 argument, channel name only
            except ValueError as ve:
                channel_name = args[0]

        # CASE 3: 2 arguments, channel name and interval, in that order
        if len(args) == 2:
            channel_name = args[0]
            self.interval = float(args[1])

        channel: discord.TextChannel = await converterplus.lookup_textchannel(ctx, channel_name)
        guild: discord.Guild = self.bot.get_guild(730196305124655176)
        # Look for discord-plays thread in open threads
        for thr in guild.threads:
            if thr.name == "max":
                self.max_thread = thr
                break
        # Look for thread in archived threads
        if self.max_thread == None:
            async for thr in channel.archived_threads():
                if (thr.name == "max"):
                    self.max_thread = thr
                    break
        # Create thread if can't find it
        if self.max_thread == None:
            self.max_thread = await channel.create_thread(name="max", type=discord.ChannelType.public_thread)

        # Create Max member objects
        max_id = 143524110813757440
        self.max_member: discord.Member = ctx.guild.get_member(max_id)
        if self.max_member.status == None:
            self.max_member.status = self.max_member.desktop_status
        # Start event and post current status
        self.post.change_interval(minutes=self.interval)
        self.post.start()
        # Send starting reaction
        await ctx.respond(f"👀 {self.max_thread.mention}")

        await super().start(ctx)

    async def end(self, ctx, args):
        self.post.cancel()
        await self.max_thread.archive()
        self.max_thread = None
        self.max_member = None
        await ctx.respond("\N{SEE-NO-EVIL MONKEY}")
        await super().end(ctx)

    def load(self):
        # Do nothing in this Event subclass; loading tasks not implemented
        pass

    def get_dict(self):
        parent = super().get_dict()
        parent.update({
            "interval": self.interval
        })
        return parent

    async def on_presence_update(self, before: discord.Member, after: discord.Member):
        if self.is_active:
            # Get Max's info only
            if before.id == self.max_member.id:
                if before.guild.id == 730196305124655176:
                    if (before.is_on_mobile() and after.is_on_mobile()) \
                            or (before.status != discord.Status.online and after.status == discord.Status.online) \
                            or (before.status != discord.Status.offline and after.status == discord.Status.offline) \
                            or (before.status != discord.Status.idle and after.status == discord.Status.idle) \
                            or (before.status != discord.Status.dnd and after.status == discord.Status.dnd):
                        self.post.restart()
