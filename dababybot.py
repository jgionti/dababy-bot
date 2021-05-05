import logging
logging.basicConfig(level=logging.INFO)
import discord
from discord.ext import commands
from cogs import timer

bot = commands.Bot('$', intents=discord.Intents.all())
extensions = [
    "cogs.general",
    "cogs.roles",
    "cogs.converterplus"]
for ext in extensions:
    bot.load_extension(ext)

# "static" variables
# Placed here to prevent overwrite on $reload
bot.token = "ODE3NTEzOTA5NzY1Mjc1Njk5.YEKnKA.q71BQ0XqCLk4uh2Q8ccwk9W26gw"       # Discord token             str
bot.phrases = []                                                                # Dababy lines              List[str]
bot.persona = []                                                                # Persona message cache     List[str]
bot.pogs = {}                                                                   # Map of id:pogs            Dict{int:bool}
bot.timer_enabled = False                                                       # Whether Timer is on       bool

# Prints if successfully logged in
@bot.event
async def on_ready():
    activity = discord.Activity(name="you. Run.")
    activity.type = discord.ActivityType(2)
    await bot.change_presence(activity=activity)
    for guild in bot.guilds:
        await guild.me.edit(nick="DaBaby")
    print("\nLogged in as\n" + bot.user.name + "\n" + str(bot.user.id) + "\n------")


# Error reactions
@bot.event
async def on_command_error(ctx, error):
    error_type = error.__class__.__name__
    
    if error_type == "MemberNotFound":
        await ctx.message.add_reaction("\N{CROSS MARK}")
        await ctx.message.add_reaction("\N{MAN}")        
    elif error_type == "RoleNotFound":
        await ctx.message.add_reaction("\N{CROSS MARK}")
        await ctx.message.add_reaction("\N{VIDEO GAME}")
    elif error_type == "MissingPermissions":
        await ctx.message.add_reaction("\N{CROSS MARK}")
    elif error_type == "CommandNotFound":
        await ctx.message.add_reaction("\N{BLACK QUESTION MARK ORNAMENT}")
        await ctx.message.add_reaction("\N{THINKING FACE}")
    elif error_type == "MissingRequiredArgument":
        await ctx.message.add_reaction("\N{BLACK QUESTION MARK ORNAMENT}")
        await ctx.message.add_reaction("\N{PINCHING HAND}")
    elif error_type == "CommandOnCooldown":
        await ctx.message.add_reaction("\N{CROSS MARK}")
        await ctx.message.add_reaction("\N{STOPWATCH}")
    else:
        await ctx.message.add_reaction("\N{BLACK QUESTION MARK ORNAMENT}")
        await ctx.message.add_reaction("\N{HEAVY EXCLAMATION MARK SYMBOL}")

    raise error


# Bot only takes commands from #dababy
@bot.event
async def on_message(message):
    # Misc. operations before command processing
    await bot.get_cog("General").on_message_helper(message)
    # Command processing
    if message.channel.name == "dababy":
        was_enabled = bot.timer_enabled
        if bot.timer_enabled and message.content[0] == bot.command_prefix:
            t = timer.Timer()
            t.start()
        await bot.process_commands(message)
        if bot.timer_enabled and was_enabled and message.content[0] == bot.command_prefix:
            t.stop()
            await message.channel.send("That command took me " + str(round(t.get_time(),4)) + " seconds!")



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
    await ctx.guild.me.edit(nick="DaBaby")
    for ext in extensions:
        bot.reload_extension(ext)
    await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")


bot.run(bot.token)
