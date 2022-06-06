import os
from os.path import isfile, join

import discord
from discord.ext import commands

from lib.database import Database

class DaBabyBot(commands.Bot):
    def __init__(self):
        super().__init__("$", intents=discord.Intents.all())

        # Load data from .env
        self.token = os.environ.get("BOT_TOKEN")

        # Other global variables
        self.phrases = []
        """List[str] - /dababy phrases"""
        self.pogs = {}
        """Dict{int:bool} - Map of id:pogs for /pog"""
        self.db = Database()
        """Bot database for maintaining persistent data"""

        # Load all cogs from 'cogs' folder
        dir = join(os.getcwd(), "cogs")
        extensions = []
        for file in os.listdir(dir):
            if isfile(join(dir, file)) and not file.startswith("_"):
                extensions.append("cogs." + file.removesuffix(".py"))
        for ext in extensions:
            self.load_extension(ext)
