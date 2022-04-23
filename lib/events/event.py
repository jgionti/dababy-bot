import discord
from typing import List

class Event:
    """Base class for server events.
    """
    def __init__(self, bot, aliases = []):
        self.aliases = aliases
        self.is_active = False
        self.ctx = None
        self.bot = bot

    async def toggle(self, ctx, args: List[str] = ...):
        """Toggles the event (start if inactive or end if active).

        args is an optional list of space-separated strings.
        """
        if not self.is_active:
            await self.start(ctx, args)
        else:
            await self.end(ctx, args)

    async def start(self, ctx, args: List[str] = ...):
        """Coroutine to start the event.

        args is an optional list of space-separated strings.
        """
        self.is_active = True
        self.ctx = ctx

    async def end(self, ctx, args: List[str] = ...):
        """Coroutine to end the event.
        """
        self.is_active = False

    async def on_message(self, message: discord.Message):
        """Coroutine to execute with the on_message() event.
        """
        pass

    async def on_presence_update(self, before: discord.Member, after: discord.Member):
        """Coroutine to execute with the on_presence_update() event.
        """
        pass
    