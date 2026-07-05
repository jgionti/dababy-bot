import os
from os.path import isfile, join
from typing import List

import discord
from discord.ext import commands

from src import converterplus
from src.constants import GLOBAL_COMMANDS
from src.database import Database

class DaBabyBot(commands.Bot):
    def __init__(self):
        super().__init__("$", intents=discord.Intents.all())

    async def init(self):
        # Load data from .env
        self.token = os.environ.get("BOT_TOKEN")

        # Other global variables
        self.phrases: List[str] = []
        """/dababy phrases"""
        self.pogs: dict[int, bool] = {}
        """Map of id:pogs for /pog"""
        self.db = Database()
        """Bot database for maintaining persistent data"""

        # Load all cogs from 'cogs' folder
        dir = join(os.getcwd(), "src", "cogs")
        extensions = []
        for file in os.listdir(dir):
            if isfile(join(dir, file)) and not file.startswith("_"):
                extensions.append("src.cogs." + file.removesuffix(".py"))
        for ext in extensions:
            await self.load_extension(ext)

        self.tree.interaction_check = self.interaction_check

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if (interaction.channel.name == "dababy" 
                or interaction.data["name"] in GLOBAL_COMMANDS):
            return True
        else:
            chn = await converterplus.lookup_textchannel(interaction, "dababy")
            await interaction.response.send_message(f"❌ Use commands in {chn.mention}!", ephemeral=True)
            return False
