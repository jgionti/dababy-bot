import os
from os.path import isfile, join

import discord
from discord.ext import commands


def bot_init():
    bot = commands.Bot("$", intents=discord.Intents.all())

    # Load all cogs in 'cogs' folder
    dir = join(os.getcwd(), "cogs")
    extensions = []
    for file in os.listdir(dir):
        if isfile(join(dir, file)) and not file.startswith("_"):
            extensions.append("cogs." + file.removesuffix(".py"))
    for ext in extensions:
        bot.load_extension(ext)

    # Load data from .env
    token = os.environ.get("BOT_TOKEN")

    # "static" variables
    # Placed in bot to prevent overwrite on $reload
    bot.token = token   # Discord token             str
    bot.phrases = []    # Dababy lines              List[str]
    bot.pogs = {}       # Map of id:pogs            Dict{int:bool}

    return bot

# Initialize bot
bot: commands.Bot = bot_init()

# Prints if successfully logged in
@bot.event
async def on_ready():
    activity = discord.Activity(name="you. Run.", type=discord.ActivityType.listening)
    await bot.change_presence(activity=activity)
    for guild in bot.guilds:
        await guild.me.edit(nick="DaBaby")
    print("\nLogged in as\n" + bot.user.name + "\n" + str(bot.user.id) + "\n------")

@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, error: Exception):
    error_smol = str(error)
    if ctx.interaction is not None:
        await ctx.respond(f"Uh oh! Error!\n```fix\n{error_smol}```")
    raise error

@bot.event
async def on_interaction(interaction: discord.Interaction):
    global_cmds = ["poll", "role"]
    if (interaction.channel.name == "dababy" or
            interaction.data["name"] in global_cmds):
        await bot.process_application_commands(interaction)
    else:
        chn = await commands.TextChannelConverter().convert(await bot.get_application_context(interaction), "dababy")
        await interaction.response.send_message(f"❌ Use commands in{chn.mention}!", ephemeral=True)

# Start the bot
bot.run(bot.token)
