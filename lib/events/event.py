from typing import List

import discord


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

    def save(self):
        """Write class contents to the database.
        """
        data = self.get_dict()
        self.bot.db.write("events", self.aliases[0], data)

    def load(self):
        """Read class contents from the database.
        """
        data = self.bot.db.read("events", self.aliases[0])
        # If document found, set all attributes to its values
        if data:
            for k, v in data.items():
                setattr(self, k, v)
        # If document not in collection, add empty version to it
        else:
            self.save()

    def get_dict(self):
        """Get class attributes in dictionary form.

        Subclasses should update the `super()` dict.
        """
        return {"is_active": self.is_active}

    async def on_message(self, message: discord.Message):
        """Coroutine to execute with the on_message() event.
        """
        pass

    async def on_presence_update(self, before: discord.Member, after: discord.Member):
        """Coroutine to execute with the on_presence_update() event.
        """
        pass
    