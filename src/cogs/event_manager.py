from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands, tasks

from src.constants import GUILD_IDS
import src.events.event_factory as event_factory
from src import autocomplete

#####################
#    eventmanager   #
#####################
# Commands and frameworks for starting/maintaining server events
# Mostly admin only commands

class EventManager(commands.Cog):
    def __init__(self, bot: commands.Bot):
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
    @app_commands.command()
    @app_commands.guilds(*GUILD_IDS)
    @app_commands.describe(
        event="Event to toggle, or 'stop' to end all events.",
        args="Space-separated event arguments."
    )
    @app_commands.autocomplete(event=autocomplete.get_server_events)
    @app_commands.checks.has_any_role("Admin", "DaBaby")
    async def event(self, interaction: discord.Interaction,
        event: str,
        args: Optional[str]
    ):
        """Start an event or stop all running events."""
        # Check if stop
        if event.lower() == "stop":
            for e in self.events:
                if e.is_active:
                    await e.end(interaction, [])
                    e.save()
            await interaction.response.send_message("✅ Stopped all events!")
            return

        # Write arguments
        a = []
        if (len(args) > 0):
            a = args.split()

        # Search for event and toggle it
        found = False
        for e in self.events:
            if event.lower() in e.aliases:
                await e.toggle(interaction, a)
                e.save()
                found = True
                break

        if not found:
            await interaction.response.send_message("\N{CROSS MARK} Event not found! 🤡", ephemeral = True)

async def setup(bot: commands.Bot):
    await bot.add_cog(EventManager(bot))
