import logging
logging.basicConfig(level=logging.INFO)
import discord
from discord.ext import commands

bot: commands.Bot = commands.Bot('$', intents=discord.Intents.all())
extensions = [
    "cogs.general",
    "cogs.roles",
    "cogs.converterplus",
    "cogs.events",
    "cogs.voice"]
for ext in extensions:
    bot.load_extension(ext)

# "static" variables
# Placed here to prevent overwrite on $reload
bot.token = "ODE3NTEzOTA5NzY1Mjc1Njk5.YEKnKA.q71BQ0XqCLk4uh2Q8ccwk9W26gw"       # Discord token             str
bot.phrases = []                                                                # Dababy lines              List[str]
bot.persona = []                                                                # Persona message cache     List[str]
bot.pogs = {}                                                                   # Map of id:pogs            Dict{int:bool}

# Prints if successfully logged in
@bot.event
async def on_ready():
    activity = discord.Activity(name="you. Run.")
    activity.type = discord.ActivityType(2)
    await bot.change_presence(activity=activity)
    for guild in bot.guilds:
        await guild.me.edit(nick="DaBaby")
    print("\nLogged in as\n" + bot.user.name + "\n" + str(bot.user.id) + "\n------")

# Error message display
@bot.event
async def on_command_error(ctx, error):
    msg_sec = 10
    emoji = "\N{THUMBS UP SIGN}"
    error_smol = error.__class__.__name__ + ": " + str(error)
    error_str = ("Uh oh! Error!\n\n" + error_smol + "\n\n"
                "This error message will be deleted in " + str(msg_sec) + " seconds.\n" +
                "Or click on the " + emoji + " reaction to keep this message.")
    msg: discord.Message = await ctx.send(error_str, reference=ctx.message, mention_author=False)
    await msg.add_reaction(emoji)

    def check(reaction, user):
        return reaction.emoji == emoji and user != ctx.me
    try: react, user = await bot.wait_for("reaction_add", check=check, timeout=msg_sec)
    except: react = None
    
    if react and react.count > 1:
        await msg.clear_reactions()
        await msg.edit(content="Uh oh! Error! "+error_smol)
    else:
        await msg.delete()
        await ctx.message.add_reaction("\N{CROSS MARK}")

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
    extensions.append(full_ext)
    await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")

# Unloads a cog
@bot.command(help = "Admin only. Unloads a cog.")
@commands.has_permissions(administrator=True)
async def unload(ctx, ext: str):
    full_ext = "cogs." + ext
    bot.unload_extension(full_ext)
    extensions.remove(full_ext)
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
