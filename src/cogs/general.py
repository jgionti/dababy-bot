import datetime
import random
from typing import List, Literal, Optional

import discord
from discord import app_commands
from discord.ext import commands
from src import autocomplete, converterplus, chance
from src.constants import GUILD_IDS
from src.dababy_bot import DaBabyBot

#####################
#      general      #
#####################
# Main functionalities
# Interactions mainly through text

class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: DaBabyBot = bot

    #######################
    #  HELPER FUNCTIONS   #
    #######################

    # Get the bot phrases using phrases.txt
    async def init_phrases(self) -> List[str]:
        print("Initializaing phrases...")
        phrases_list = []
        file = open("resources/phrases.txt", "r", encoding="utf-8")
        for line in file:
            phrases_list.append(line.rstrip())
        print("Done!")
        return phrases_list
        
    # Get the list of online members for the guild to which the context belongs
    async def get_online_members(self, interaction: discord.Interaction) -> List[discord.Member]:
        online_members = []
        for mem in interaction.guild.members:
            if mem.status != discord.Status.offline:
                online_members.append(mem)
        return online_members

    # Get the pog value for a particular member, then attempt to swap it
    # Return: bool
    async def get_pog(self, member: discord.Member):
        d = self.bot.pogs
        if member.id not in d:
            d[member.id] = chance.chance(50)
        if chance.chance(25):
            d[member.id] = not d[member.id]
        return d[member.id]

    #######################
    #       COMMANDS      #
    #######################

    # Basic command, useful for testing connection
    @app_commands.command()
    @app_commands.guilds(*GUILD_IDS)
    async def ping(self, interaction: discord.Interaction):
        """Displays the bot's latency."""
        await interaction.response.send_message("Pong! Latency is " + str(int(self.bot.latency*1000)) + " ms.")
    
    # Sends a random dababy line
    @app_commands.command()
    @app_commands.guilds(*GUILD_IDS)
    @app_commands.describe(
        message="What you want to say to DaBaby"
    )
    async def dababy(self, interaction: discord.Interaction,
        message: Optional[str]
    ):
        """Sends a random DaBaby phrase."""
        msg = ""
        callback = None
        if message:
            msg += f"`{interaction.user.display_name} said:` {message}\n\n"
        if not self.bot.phrases:
            callback = await interaction.response.send_message("Loading...")
            self.bot.phrases = await self.init_phrases()
        msg += random.choice(self.bot.phrases)
        if callback is not None:
            await callback.resource.edit(content=msg)
        else: await interaction.response.send_message(msg)

    # States that a random online member is suspicious, slightly weighted toward Dante
    @app_commands.command()
    @app_commands.guilds(*GUILD_IDS)
    async def sus(self, interaction: discord.Interaction):
        """States that a random server member is suspicious."""
        members = await self.get_online_members(interaction)
        dante = interaction.guild.get_member(203300119557308417)
        if dante in members:
            members.append(dante)
            members.append(dante)
            members.append(dante)
        num = chance.select_with_remainder(0.5, 5)
        name = random.choice(members).display_name
        if num == 0:
            # Mega sus
            msg = "Uh, oh no... this can't be right...\n**" + name + "** is **MEGA SUS!**"
            fil = discord.File("resources/MegaSus.mp4")
        elif num == 1:
            # Super sus
            msg = "Yo, emergency meeting! **" + name + "** is **super sus!**"
            fil = discord.File("resources/SuperSus.jpg")
        else:
            # Normal sus
            msg = "Ayo! **" + name + "** is sus!"
            fil = discord.File("resources/JermaSus.jpg")
        await interaction.response.send_message(content=msg, file=fil)

    # States whether a given member is poggers
    @app_commands.command()
    @app_commands.guilds(*GUILD_IDS)
    @app_commands.describe(
        member="Server member to be judged by DaBaby"
    )
    @app_commands.autocomplete(member=autocomplete.get_members)
    async def pog(self, interaction: discord.Interaction,
        member: Optional[str] = "me"
    ):
        """States whether a server member is poggers. Leave blank or type \"me\" to test yourself."""
        mem = await converterplus.lookup_member(interaction, member)
        is_pog = await self.get_pog(mem)
        if is_pog:
            await interaction.response.send_message(mem.display_name + " is **pog!** This is good news!!!")
        else: await interaction.response.send_message(mem.display_name + " is **not pog!** That's disgusting!!!")

    # Rock paper scissors game
    @app_commands.command()
    @app_commands.guilds(*GUILD_IDS)
    async def rps(self, interaction: discord.Interaction,
        choice: Literal["rock", "paper", "scissors"]
    ):
        """Play rock paper scissors with DaBaby!"""
        color = discord.Color.light_gray()
        is_tie = False
        bot_wins = True
        my_int = random.randint(1,3) # 1,2,3 = Rock, Paper, Scissors
        p_int = 0
        int_to_rps = {0: choice+"\N{BUST IN SILHOUETTE}", 1: "Rock\N{ROCK}",\
            2: "Paper\N{SCROLL}", 3: "Scissors\N{BLACK SCISSORS}"}

        if choice.lower() in ["rock", "r", "1"]:
            p_int = 1
        elif choice.lower() in ["paper", "p", "2"]:
            p_int = 2
        elif choice.lower() in ["scissors", "s", "3", "scissor"]:
            p_int = 3

        string = "You chose: **" + int_to_rps[p_int] + "**\n"
        string += "I chose: **" + int_to_rps[my_int] + "**\n\n"
        if p_int == 0:
            bot_wins = chance.chance(50)
        elif my_int == 1:
            if p_int == 1: is_tie = True
            if p_int == 2: bot_wins = False
            if p_int == 3: bot_wins = True
        elif my_int == 2:
            if p_int == 2: is_tie = True
            if p_int == 3: bot_wins = False
            if p_int == 1: bot_wins = True
        elif my_int == 3:
            if p_int == 3: is_tie = True
            if p_int == 1: bot_wins = False
            if p_int == 2: bot_wins = True

        if is_tie:
            string += "**It's a tie!**"
        elif bot_wins:
            string += "**" + int_to_rps[my_int] + "** beats **" + int_to_rps[p_int] + "**!\nI win! Let's go!"
            color = discord.Color.red()
        else:
            string += "**" + int_to_rps[p_int] + "** beats **" + int_to_rps[my_int]+ "**!\n"\
                + interaction.user.display_name + " wins!"
            color = discord.Color.green()

        await interaction.response.send_message(embed=discord.Embed(description=string, color=color))

async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))
