import datetime
import random
from typing import List, Literal, Optional

import discord
from discord import app_commands
from discord.ext import commands
from src import autocomplete, converterplus, chance
from src.constants import GUILD_IDS

#####################
#      general      #
#####################
# Main functionalities
# Interactions mainly through text

class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

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

    # Get every message from up to 30 days ago
    async def get_message_cache(self, interaction: discord.Interaction, days: int=30) -> List[discord.Message]:
        async with interaction.channel.typing():
            message_cache = []
            for channel in interaction.guild.text_channels:
                perm = channel.permissions_for(interaction.guild.me)
                if perm.read_message_history == True and perm.read_messages == True:
                    after = datetime.datetime.today() - datetime.timedelta(days=days)
                    history = [message async for message in channel.history(after=after)]
                    for message in history:
                        message_cache.append(message)
        return message_cache

    # Get the number of messages a member recently sent across all visible channels
    # Return: (count, total)
    async def get_message_tuple(self, interaction: discord.Interaction, member: discord.Member) -> tuple[int, int]:
        count = 0
        total = 0
        message_cache = await self.get_message_cache(interaction)
        for message in message_cache:
            total += 1
            if message.author == member:
                count += 1
        return (count, total)
        
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

    # Convert the List[Role] of a member to a formatted string
    # Return: str
    async def get_role_string(self, member: discord.Member):
        role_str = ""
        count = 0
        role_list = member.roles
        role_list.reverse()
        role_list.pop()
        for role in role_list:
            role_str += role.mention + " "
            count += 1
            if count % 4 == 0:
                role_str += "\n"
        return role_str

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

    # Displays info about a particular member
    @app_commands.command()
    @app_commands.guilds(*GUILD_IDS)
    @app_commands.describe(
        member="Server member to get info about"
    )
    @app_commands.autocomplete(member=autocomplete.get_members)
    async def info(self, interaction: discord.Interaction, 
        member: Optional[str] = "me"
    ):
        """Displays info about a server member. Leave blank or type \"me\" to test yourself."""
        async with interaction.channel.typing():
            mem: discord.Member = await converterplus.lookup_member(interaction, member)
            callback = await interaction.response.send_message("Lemme look! (Fetching messages...)")
            msg_tuple = await self.get_message_tuple(interaction, mem)
            msg_density = msg_tuple[0]/msg_tuple[1]
            role_str = await self.get_role_string(mem)
            embed = discord.Embed(color = mem.top_role.color, title=(mem.name+"#"+str(mem.discriminator)))
            embed.set_image(url=mem.display_avatar.with_size(128))
            embed.add_field(name="Mention", value=mem.mention)
            embed.add_field(name="Recent Messages", value=(str(msg_tuple[0])))
            embed.add_field(name="Message Density", value=(str(round(msg_density*100, 2))+"%"))
            embed.add_field(name="Roles", value=role_str, inline=False)
            embed.set_footer(text="Recent Messages are counted over the past 30 days.")
            await callback.resource.edit(content="", embed=embed)

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
