import discord
from discord.ext import commands

from lib.dababy_bot import DaBabyBot

# Initialize bot
bot = DaBabyBot()

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
