import random

import discord
from lib import converterplus
from lib.events.event import Event


class CapEvent(Event):
    def __init__(self, bot):
        super().__init__(bot, aliases=["cap"])
        self.bias = []

    async def start(self, ctx, args):
        await ctx.respond('🧢')
        brank = converterplus.lookup_member(ctx, "290153703808434176")
        max = converterplus.lookup_member(ctx, "143524110813757440")
        self.bias = [brank, max]
        await super().start(ctx)

    async def end(self, ctx, args):
        await super().end(ctx)
        await ctx.respond("🚫🧢")

    async def on_message(self, message: discord.Message):
        if self.is_active:
            cond = (random.randint(0, 100) < 10) or \
                    ((random.randint(0, 100) < 50) and message.author in self.bias)
            if cond:
                await message.add_reaction('🧢')
