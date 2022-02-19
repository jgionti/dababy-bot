import discord
from discord.ext import commands
import youtube_search

#####################
#    autocomplete   #
#####################
# Introduces functions for autocomplete purposes

def _autocomplete(arr, input):
    return [s for s in arr if s.lower().startswith(input.lower())]

def get_members(ctx: discord.AutocompleteContext):
    arr = []
    member: discord.Member
    for member in ctx.interaction.guild.members:
        arr.append(member.name)
        if (member.name != member.display_name):
            arr.append(member.display_name)
    arr.append("me")
    return _autocomplete(arr, ctx.options["member"])

def get_roles(ctx: discord.AutocompleteContext):
    arr = []
    role: discord.Role
    for role in ctx.interaction.guild.roles:
        if role.position > 0:
            arr.append(role.name)
    return _autocomplete(arr, ctx.options["role"])

def get_yt(ctx: discord.AutocompleteContext):
    arr = []
    search = ctx.options["url"]
    ytsearch = youtube_search.YoutubeSearch(search, max_results=5)
    for vid in ytsearch.videos:
        arr.append(vid["id"] + " | " + vid["channel"] + ": \"" + vid["title"] + '\"')
    
    return _autocomplete(arr, "")
    