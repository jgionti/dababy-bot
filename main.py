import os
import discord
from discord.ext import commands

# Initialize bot and cogs
bot: commands.Bot = commands.Bot(commands.when_mentioned_or("$"), intents=discord.Intents.all())
extensions = [
    "cogs.general",
    "cogs.roles",
    "cogs.converterplus",
    "cogs.events",
    "cogs.voice"]
for ext in extensions:
    bot.load_extension(ext)

# Load data from .env
token = os.environ.get("BOT_TOKEN")

# "static" variables
# Placed here to prevent overwrite on $reload
bot.token = token   # Discord token             str
bot.phrases = []    # Dababy lines              List[str]
bot.persona = []    # Persona message cache     List[str]
bot.pogs = {}       # Map of id:pogs            Dict{int:bool}

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
#@bot.event
async def on_command_error(ctx, error):
    msg_sec = 20
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
#@bot.event
async def on_message(message):
    if message.channel.name == "dababy":
        await bot.process_commands(message)

@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, error: Exception):
    error_smol = str(error)
    await ctx.respond("Uh oh! Error!\n"+error_smol, delete_after=5)
    raise error

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.channel.name == "dababy":
        await bot.process_application_commands(interaction)
    else:
        chn = await commands.TextChannelConverter().convert(await bot.get_application_context(interaction), "dababy")
        await interaction.response.send_message("❌ Use commands in"+chn.mention+"!", ephemeral=True)

# Loads a cog
#@bot.slash_command(guild_ids = [730196305124655176])
@discord.permissions.has_role("Admin")
async def load(ctx, ext: str):
    """Loads a cog."""
    full_ext = "cogs." + ext
    bot.load_extension(full_ext)
    extensions.append(full_ext)
    await ctx.respond("Loaded "+ext, ephemeral=True)

# Unloads a cog
#@bot.slash_command(guild_ids = [730196305124655176])
@discord.permissions.has_role("Admin")
async def unload(ctx, ext: str):
    """Unloads a cog."""
    full_ext = "cogs." + ext
    bot.unload_extension(full_ext)
    extensions.remove(full_ext)
    await ctx.respond("Unloaded "+ext, ephemeral=True)

# Reloads all cogs
#@bot.slash_command(guild_ids = [730196305124655176])
@discord.permissions.has_role("Admin")
async def reload(ctx):
    """Reloads most commands."""
    await ctx.guild.me.edit(nick="DaBaby")
    for ext in extensions:
        bot.reload_extension(ext)
    await ctx.respond("Reloaded!", ephemeral=True)

# Start the bot
bot.run(bot.token)
