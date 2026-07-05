from typing import List

import discord
from discord import app_commands

import src.events.event_factory as event_factory
from src.events.event import Event

#####################
#    autocomplete   #
#####################
# Introduces functions for autocomplete purposes

def _autocomplete(arr: List[str], current: str) -> List[app_commands.Choice[str]]:
    return [
        app_commands.Choice(name=s, value=s)
        for s in arr if current.lower() in s.lower()
    ]

async def get_members(interaction: discord.Interaction, current: str):
    arr = []
    member: discord.Member
    for member in interaction.guild.members:
        arr.append(member.name)
        if (member.name != member.display_name):
            arr.append(member.display_name)
    arr.append("me")
    return _autocomplete(arr, current)

async def get_roles(interaction: discord.Interaction, current: str):
    arr = []
    role: discord.Role
    for role in interaction.guild.roles:
        if role.position > 0:
            arr.append(role.name)
    return _autocomplete(arr, current)

async def get_server_events(interaction: discord.Interaction, current: str):
    arr = []
    arr.append("stop")
    events = event_factory.get_events(interaction.client)
    e: Event
    for e in events:
        arr += e.aliases
    return _autocomplete(arr, current)
    