import discord
from src import converterplus, chance
from src.database import Database
from src.events.event import Event


class CapEvent(Event):
    def __init__(self, bot):
        super().__init__(bot, aliases=["cap"])
        self.bias = []

    async def start(self, interaction, args):
        await interaction.response.send_message('🧢')
        brank = converterplus.lookup_member(interaction, "290153703808434176")
        max = converterplus.lookup_member(interaction, "143524110813757440")
        self.bias = [brank, max]
        await super().start(interaction)

    async def end(self, interaction, args):
        await super().end(interaction)
        await interaction.response.send_message("🚫🧢")

    async def on_message(self, message: discord.Message):
        if self.is_active:
            cond = (chance.chance(10) and message.author not in self.bias) or \
                    (chance.chance(50) and message.author in self.bias)
            if cond:
                await message.add_reaction('🧢')
