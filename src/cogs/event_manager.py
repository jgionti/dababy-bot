import discord
from discord.ext import commands, tasks
from src import autocomplete
from src.constants import GUILD_IDS
import src.events.event_factory as event_factory

#####################
#    eventmanager   #
#####################
# Commands and frameworks for starting/maintaining server events
# Mostly admin only commands

class EventManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Get events and load them
        self.events = event_factory.get_events(bot)
        self.load()

        # Start autosaving
        # self.autosave.start()

    #######################
    #  HELPER FUNCTIONS   #
    #######################

    @tasks.loop(minutes=60)
    async def autosave(self):
        # Task not currently active; behavior with Heroku is unknown
        self.save()

    def save(self):
        for e in self.events:
            e.save()

    def load(self):
        for e in self.events:
            e.load()

    # Listener for user messages
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        for e in self.events:
            await e.on_message(message)

    # Listener for change in member info
    @commands.Cog.listener()
    async def on_presence_update(self, before: discord.Member, after: discord.Member):
        for e in self.events:
            await e.on_presence_update(before, after)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        for e in self.events:
            await e.on_voice_state_update(member, before, after)

    #######################
    #       COMMANDS      #
    #######################

    # Main event command
    @commands.slash_command(guild_ids = GUILD_IDS)
    @commands.has_any_role("Admin", "DaBaby")
    async def event(self, ctx,
        event: discord.Option(str, "Event to toggle, or 'stop' to end all events.", autocomplete = autocomplete.get_server_events),
        args: discord.Option(str, "Space-separated event arguments.", required = False, default = "")
    ):
        """Start an event or stop all running events."""
        # Check if stop
        if event.lower() == "stop":
            for e in self.events:
                if e.is_active:
                    await e.end(ctx, [])
                    e.save()
            await ctx.respond("✅ Stopped all events!")
            return

        # Write arguments
        a = []
        if (len(args) > 0):
            a = args.split()

        # Search for event and toggle it
        found = False
        for e in self.events:
            if event.lower() in e.aliases:
                await e.toggle(ctx, a)
                e.save()
                found = True
                break

        if not found:
            await ctx.respond("\N{CROSS MARK} Event not found! 🤡", ephemeral = True)

def setup(bot):
    bot.add_cog(EventManager(bot))
