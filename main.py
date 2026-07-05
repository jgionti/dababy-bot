import asyncio
import discord
from discord.ext import commands

from src.dababy_bot import DaBabyBot
from src.constants import GLOBAL_COMMANDS, GUILD_IDS

# Initialize bot
bot = DaBabyBot()
asyncio.run(bot.init())

# Prints if successfully logged in
@bot.event
async def on_ready():
    activity = discord.Activity(name="you. Run.", type=discord.ActivityType.listening)
    await bot.change_presence(activity=activity)
    await bot.tree.sync()
    for guild in bot.guilds:
        await guild.me.edit(nick="DaBaby")
        if guild.id in GUILD_IDS:
            await bot.tree.sync(guild=guild)
    print("\nLogged in as\n" + bot.user.name + "\n" + str(bot.user.id) + "\n------")

@bot.event
async def on_application_command_error(interaction: discord.Interaction, error: Exception):
    error_smol = str(error)
    if interaction is not None:
        await interaction.response.send_message(f"Uh oh! Error!\n```fix\n{error_smol}```")
    raise error

# Start the bot
bot.run(bot.token)
