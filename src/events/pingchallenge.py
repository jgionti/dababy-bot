import asyncio

import discord
from src.events.event import Event


class PingChallengeEvent(Event):
    """Event class for the Mr. Ping Challenge.

    The first user to ping @everyone in their next 19 messages wins.
    """
    def __init__(self, bot: discord.Bot):
        super().__init__(bot=bot, aliases=["mrpingchallenge"])
        self.ping_map = {}
        self.ping_winner = None
        
    async def start(self, ctx, args):
        await super().start(ctx)
        msg = "The Mr. Ping Challenge has started! The first user to complete it gets a prize!"
        await ctx.respond(content=msg, file=discord.File("resources/MrPingChallenge.png"))

    async def end(self, ctx, args):
        if (ctx == None):
            ctx = self.ctx
        if self.ping_winner is None:
            await ctx.respond("The Mr. Ping Challenge is over! Nobody won! 🤡")
        else:
            await ctx.send("Congratulations, " + self.ping_winner.mention + "! You've won the Mr. Ping Challenge! Now for your prize...")
            await asyncio.sleep(5)
            await self.bot.get_cog("Roles").brazil(ctx, str(self.ping_winner.id), time=300, reason="You pinged everyone 19 times!")
        self.ping_map = {}
        self.ping_winner = None
        await super().end(ctx)

    def get_dict(self):
        parent = super().get_dict()
        parent.update({
            "ping_map" : self.ping_map
        })
        return parent

    async def on_message(self, message: discord.Message):
        if self.is_active:
            # If author uses @everyone,
            if message.mention_everyone:
                # Add 1 to their count
                if message.author.id in self.ping_map:
                    self.ping_map[message.author.id] += 1
                else: self.ping_map[message.author.id] = 1
                # Win condition check
                if self.ping_map[message.author.id] == 19:
                    self.ping_winner = message.author
                    await self.end(None, None)
            # If author doesn't @everyone, streak was broken
            elif message.author.id in self.ping_map:
                self.ping_map[message.author.id] = 0
