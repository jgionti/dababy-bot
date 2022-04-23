import discord
from lib.events.event import Event
from lib import converterplus

class MaxIsOnlineEvent(Event):
    """Event class for the Max is Online event.

    Every time Cyanide#7815 changes status, the bot sends a gif
    corresponding to his latest status into the #max thread.
    """
    def __init__(self, bot):
        super().__init__(bot, aliases=["maxisonline"])
        self.has_max_event = False
        self.max_thread = None
        self.max_member = None
        self.gif_str = ""

    # Update self.gif_str and post status of a member to #max
    async def _post_status(self, member: discord.Member):
        if member.status == discord.Status.online:
            self.gif_str = "https://tenor.com/view/max-online-dmc-devil-may-cry-dante-gif-21772253"
        elif member.status == discord.Status.offline:
            self.gif_str = "https://tenor.com/view/dmc-devil-may-cry-nero-max-max-is-offline-gif-21779492"
        elif member.status == discord.Status.idle:
            self.gif_str = "https://cdn.discordapp.com/attachments/290272452427251723/912784098014142504/dmc-max-away.gif"
        elif member.status == discord.Status.dnd:
            self.gif_str = "https://cdn.discordapp.com/attachments/290272452427251723/912784109925982308/dmc-max-dnd.gif"
        await self.max_thread.send(self.gif_str)

    async def start(self, ctx, args):
        # Create new max thread in #general if it doesn't already exist
        channel: discord.TextChannel = await converterplus.lookup_textchannel(ctx, "general")
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
        await self._post_status(self.max_member)
        # Send starting reaction
        await ctx.respond("\N{EYES} " + self.max_thread.mention)

        await super().start(ctx)

    async def end(self, ctx, args):
        await self.max_thread.archive()
        self.max_thread = None
        self.max_member = None
        await ctx.respond("\N{SEE-NO-EVIL MONKEY}")
        await super().end(ctx)

    async def on_presence_update(self, before: discord.Member, after: discord.Member):
        if self.is_active:
            # Get Max's info only
            if before.id == self.max_member.id:
                if before.guild.id == 730196305124655176:
                    if (before.status != discord.Status.online and after.status == discord.Status.online)\
                        or (before.status != discord.Status.offline and after.status == discord.Status.offline)\
                        or (before.status != discord.Status.idle and after.status == discord.Status.idle)\
                        or (before.status != discord.Status.dnd and after.status == discord.Status.dnd):
                        await self._post_status(after)