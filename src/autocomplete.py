import discord

import src.events.event_factory as event_factory
from src.events.event import Event

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

def get_server_events(ctx: discord.AutocompleteContext):
    arr = []
    arr.append("stop")
    events = event_factory.get_events(ctx.bot)
    e: Event
    for e in events:
        arr += e.aliases
    return _autocomplete(arr, ctx.options["event"])
    