import asyncio
from typing import List, Optional

import discord
from discord import app_commands
from discord.ext import commands
from src import autocomplete, converterplus, timer
from src.constants import GUILD_IDS

#####################
#       roles       #
#####################
# Autonomous role management
# Any role underneath @Brazil and above @everyone is eligible

class Roles(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.brazil_times: dict[str, float] = {}

    #######################
    #  HELPER FUNCTIONS   #
    #######################

    # Get the function to help sort get_auto_roles() with
    def role_sort(self, role: discord.Role) -> str:
        return role.name

    # Get the roles the bot should handle
    async def get_auto_roles(self, interaction: discord.Interaction) -> List[discord.Role]:
        brazil_role = await self.get_brazil_role(interaction)
        auto_roles = []
        for role in interaction.guild.roles:
            if role.position < brazil_role.position and role.position > 0:
                auto_roles.append(role)
        auto_roles.reverse()
        auto_roles.sort(key=self.role_sort)
        return auto_roles
    
    # Gets Brazil role
    async def get_brazil_role(self, interaction: discord.Interaction) -> discord.Role:
        return await converterplus.lookup_role(interaction, "Brazil")

    # Gets Brazil channel
    async def get_brazil_channel(self, interaction: discord.Interaction) -> discord.TextChannel:
        return await converterplus.lookup_textchannel(interaction, "brazil")

    # Sends target member to Brazil and informs others in #dababy and #brazil
    async def send_brazil(self, interaction: discord.Interaction, member: discord.Member, reason: str, time: float):
        brazil_role = await self.get_brazil_role(interaction)
        brazil_channel = await self.get_brazil_channel(interaction)
        await interaction.response.send_message("Get the boot. **" + member.display_name + "** is going to Brazil!")
        await member.add_roles(brazil_role)
        embed = discord.Embed(title = "Welcome to Brazil, " + member.display_name + "!",
                color = member.top_role.color)
        if reason != "":
            embed.add_field(name="You're here because...", value=reason)
        msg = ("You'll be here for " + timer.get_timestr(time) + "!\n\n"
               + "That's " + timer.get_time_offset(time).strftime("%m/%d/%Y, %H:%M:%S") + "! Enjoy!")
        embed.add_field(name="Your sentence...", value=msg, inline=False)
        await brazil_channel.send(embed=embed)

    # Remove a member from Brazil and inform others in #dababy and #brazil
    async def remove_brazil(self, interaction: discord.Interaction, member: discord.Member):
        brazil_role = await self.get_brazil_role(interaction)
        if brazil_role in member.roles:
            await member.remove_roles(brazil_role)
            msg = member.display_name + " has been freed from Brazil!"
            if interaction.response.is_done:
                await interaction.followup.send(msg)
            else:
                await interaction.response.send_message(msg)

    # Creates the embed for role info
    @staticmethod
    async def create_role_embed(role: discord.Role) -> discord.Embed:
        mems = ""
        if (len(role.members) > 0):
            for mem in role.members[:-1]:
                mems += mem.mention + ", "
            mems += role.members[-1].mention
        if (mems == ""):
            mems = "None"
        embed = discord.Embed(color=role.color, title="Role Info", description=role.mention)
        embed.add_field(name="Date Created", value=role.created_at.strftime("%m/%d/%Y"))
        embed.add_field(name="Color", value=str(role.color))
        embed.add_field(name="Members: "+str(len(role.members)), value=mems, inline=False)
        return embed

    # Displays a list of all roles that may be added/removed
    async def rolelist(self, interaction: discord.Interaction):
        role_list = await self.get_auto_roles(interaction)
        role_str = ""
        mem_count_str = ""
        for role in role_list:
            role_str += role.mention + "\n"
            mem_count_str += str(len(role.members)) + "\n"
        embed = discord.Embed(color=interaction.guild.me.color, title=f"{str(len(role_list))} Roles in {interaction.guild.name}")
        embed.add_field(name="Role", value=role_str)
        embed.add_field(name="Members", value=mem_count_str)
        embed.set_footer(text="Use /role <role> to add/remove a role.")
        await interaction.response.send_message(embed=embed)

    # View for /role buttons
    class RoleView(discord.ui.View):
        def __init__(self, role: discord.Role, allowed_roles: List[discord.Role]):
            super().__init__(timeout=600)
            self.role: discord.Role = role
            self.message: Optional[discord.Message] = None
            if role not in allowed_roles:
                self.clear_items()
                self.add_item(discord.ui.Button(label="This role cannot be added using the bot.", disabled=True, emoji="❌"))
                self.stop()

        async def on_timeout(self):
            self.clear_items()
            self.add_item(discord.ui.Button(label="Timed out! Use /role "+self.role.name.lower()+" to get or remove this role.", disabled=True, emoji="⏰"))
            await self.update()

        async def update(self):
            embed = await Roles.create_role_embed(self.role)
            await self.message.edit(embed=embed,view=self)

        @discord.ui.button(label="Get role!", style=discord.ButtonStyle.green, emoji="🤩")
        async def add_role(self, button: discord.ui.Button, interaction: discord.Interaction):
            response = ""
            if self.role not in interaction.user.roles:
                await interaction.user.add_roles(self.role)
                response = "✅ Added "+self.role.mention+"!"
            else: response = "❌ You already have "+self.role.mention+"!"
            await interaction.response.send_message(response, ephemeral=True)
            await self.update()

        @discord.ui.button(label="Remove role!", style=discord.ButtonStyle.red, emoji="💀")
        async def remove_role(self, button: discord.ui.Button, interaction: discord.Interaction):
            if self.role in interaction.user.roles:
                await interaction.user.remove_roles(self.role)
                response = "💀 Removed "+self.role.mention+"!"
            else: response = "❌ You don't have "+self.role.mention+"!"
            await interaction.response.send_message(response, ephemeral=True)
            await self.update()

    #######################
    #       COMMANDS      #
    #######################

    # Displays info about a role and the buttons to do it
    @app_commands.command()
    @app_commands.guilds(*GUILD_IDS)
    @app_commands.describe(
        role="Role to view info about"
    )
    @app_commands.autocomplete(role=autocomplete.get_roles)
    async def role(self, interaction: discord.Interaction,
        role: Optional[str]
    ):
        """Get info on a role and add/remove that role. Leave blank to see a list of roles."""
        if role is None:
            await self.rolelist(interaction)
            return

        rol = None
        try:
            rol = await converterplus.lookup_role(interaction, role)
        except commands.RoleNotFound:
            await interaction.response.send_message("Role not found! 🤡", ephemeral = True)
            return
        embed = await self.create_role_embed(rol)
        view = self.RoleView(rol, await self.get_auto_roles(interaction))
        callback = await interaction.response.send_message(embed=embed, view=view)
        view.message = callback.resource

    # Gives user the Brazil role for some time (in seconds)
    @app_commands.command()
    @app_commands.guilds(*GUILD_IDS)
    @app_commands.describe(
        member="Server member to send to Brazil.",
        time="How long to keep the member in Brazil (in seconds).",
        reason="Reason for sending member to Brazil. Use \"stop\" to remove from Brazil."
    )
    @app_commands.autocomplete(member=autocomplete.get_members)
    @app_commands.checks.has_any_role("Admin", "DaBaby")
    async def brazil(self, interaction: discord.Interaction,
        member: str,
        time: Optional[float] = 60.0,
        reason: Optional[str] = ""
    ):
        """Send a server member to Brazil for some time."""
        # Find member
        member = await converterplus.lookup_member(interaction, member)
        brazil_role = await self.get_brazil_role(interaction)

        # Remove from Brazil if already in there
        if reason.lower() == "stop":
            await interaction.response.send_message(f"Releasing {member.display_name} from Brazil (if they're in it 😅).", ephemeral = True)
            await self.remove_brazil(interaction, member)
            return

        # Check if in Brazil
        if brazil_role in member.roles:
            if member.id in self.brazil_times:
                msg = member.display_name + " has " + timer.get_time_until(self.brazil_times[member.id]) + " left in Brazil."\
                    + f" Have an admin use this command with \"stop\" as the reason."
                await interaction.response.send_message(msg)
            else:
                msg = member.display_name + " is in Brazil but shouldn't be! I'll just..."
                await interaction.response.send_message(msg)
                await self.remove_brazil(interaction, member)
            return
        
        # Send user to Brazil
        await self.send_brazil(interaction, member, reason, time)
        self.brazil_times[member.id] = timer.get_time_offset(time)
        # Wait for time, then release automatically
        await asyncio.sleep(time)
        await self.remove_brazil(interaction, member)

async def setup(bot: commands.Bot):
    await bot.add_cog(Roles(bot))
