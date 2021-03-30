import logging
logging.basicConfig(level=logging.INFO)
import discord
from discord.ext import commands

bot = commands.Bot('$', intents=discord.Intents.all())
extensions = [
    "cogs.general",
    "cogs.roles",
    "cogs.converterplus"]
for ext in extensions:
    bot.load_extension(ext)

# "static" variables:
bot.token = "ODE3NTEzOTA5NzY1Mjc1Njk5.YEKnKA.q71BQ0XqCLk4uh2Q8ccwk9W26gw"       # Discord token
bot.phrases = []                                                                # Dababy lines (List[str])
bot.pogs = {}                                                                   # Map of pogs  (Dict{int:bool})


# Prints if successfully logged in
@bot.event
async def on_ready():
    activity = discord.Activity(name="you. Run.")
    activity.type = discord.ActivityType(2)
    await bot.change_presence(activity=activity)
    print()
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.event
async def on_command_error(ctx, error):
    # todo: missing permissions
    error_type = error.__class__.__name__
    
    if error_type == "MemberNotFound":
        await ctx.message.add_reaction("\N{CROSS MARK}")
        await ctx.message.add_reaction("\N{MAN}")        
    elif error_type == "RoleNotFound":
        await ctx.message.add_reaction("\N{CROSS MARK}")
        await ctx.message.add_reaction("\N{VIDEO GAME}")
    elif error_type == "CommandNotFound":
        await ctx.message.add_reaction("\N{BLACK QUESTION MARK ORNAMENT}")
        await ctx.message.add_reaction("\N{THINKING FACE}")
    elif error_type == "MissingRequiredArgument":
        await ctx.message.add_reaction("\N{BLACK QUESTION MARK ORNAMENT}")
        await ctx.message.add_reaction("\N{PINCHING HAND}")
    else:
        await ctx.message.add_reaction("\N{BLACK QUESTION MARK ORNAMENT}")
        await ctx.message.add_reaction("\N{HEAVY EXCLAMATION MARK SYMBOL}")

    raise error

# Bot only takes commands from #dababy
@bot.event
async def on_message(message):
    if message.channel.name == "dababy":
        await bot.process_commands(message)


# Loads a cog
@bot.command(help = "Admin only. Loads a cog.")
@commands.has_permissions(administrator=True)
async def load(ctx, ext: str):
    full_ext = "cogs." + ext
    bot.load_extension(full_ext)
    await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")

# Unloads a cog
@bot.command(help = "Admin only. Unloads a cog.")
@commands.has_permissions(administrator=True)
async def unload(ctx, ext: str):
    full_ext = "cogs." + ext
    bot.unload_extension(full_ext)
    await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")

# Reloads all cogs
@bot.command(help = "Admin only. Reloads most commands.")
@commands.has_permissions(administrator=True)
async def reload(ctx):
    for ext in extensions:
        bot.reload_extension(ext)
    await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")

bot.run(bot.token)
