import os
import random
import requests
import discord
from discord.ext import commands

from src.dababy_bot import DaBabyBot
from src.constants import GUILD_IDS

#####################
#    watch2gether   #
#####################
# Create watch2gether rooms

class Watch2Gether(commands.Cog):
    def __init__(self, bot):
        self.bot: DaBabyBot = bot
        self.quip_list: list[str] = [
            "Your Watch2Gether room, madam:",
            "The room code? You got it:",
            "The room code is:",
            "You're not watching Yu-Gi-Oh videos, are you?",
            "Do not invite Max:",
            "One room code coming up:"
        ]

    @commands.slash_command(guild_ids = GUILD_IDS)
    async def w2g(self, ctx: discord.ApplicationContext,
        url: discord.Option(str, "(Optional) The URL of a video to preload to the room.", required=False)
    ):
        """Generates a Watch2Gether room so you don't have to!"""
        response = requests.post(
            url = "https://api.w2g.tv/rooms/create.json",
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            json = {
                "w2g_api_key": os.environ.get("W2G_API_KEY"),
                "share": url,
                "bg_color": "#000000",
                "bg_opacity": "50"
            },
        )
        response_json = response.json()
        streamkey: str = response_json['streamkey']
        await ctx.respond(f"{random.choice(self.quip_list)} https://w2g.tv/rooms/{streamkey}")

def setup(bot):
    bot.add_cog(Watch2Gether(bot))