import asyncio
import discord
from discord.ext import commands
from cogs import timer

#####################
#       roles       #
#####################
# Autonomous role management
# Any role underneath Brazil and above @everyone is eligible

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.brazil_times = {}

    #######################
    #  HELPER FUNCTIONS   #
    #######################

    # Get the function to help sort get_auto_roles() with
    # Return: str
    def role_sort(self, role: discord.Role):
        return role.name

    # Get the roles the bot should handle
    # Return: List[Role]
    async def get_auto_roles(self, ctx):
        dababy_role = await self.bot.get_cog("ConverterPlus").lookup_role(ctx, "DaBaby")
        brazil_role = await self.get_brazil_role(ctx)
        auto_roles = []
        for role in ctx.guild.roles:
            if role.position < dababy_role.position and role.position != brazil_role.position and role.position > 0:
                auto_roles.append(role)
        auto_roles.reverse()
        auto_roles.sort(key=self.role_sort)
        return auto_roles
    
    # Gets Brazil role
    # Return: Role
    async def get_brazil_role(self, ctx):
        return await self.bot.get_cog("ConverterPlus").lookup_role(ctx, "Brazil")

    # Gets Brazil channel
    # Return: TextChannel
    async def get_brazil_channel(self, ctx):
        return await self.bot.get_cog("ConverterPlus").lookup_textchannel(ctx, "brazil")

    # Sends target member to Brazil and informs others in #dababy and #brazil
    # Return: void
    async def send_brazil(self, ctx, member:discord.Member, reason: str, time):
        brazil_role = await self.get_brazil_role(ctx)
        brazil_channel = await self.get_brazil_channel(ctx)
        await ctx.respond("Get the boot. **" + member.display_name + "** is going to Brazil!")
        await member.add_roles(brazil_role)
        embed = discord.Embed(title = "Welcome to Brazil, " + member.display_name + "!",
                color = member.top_role.color)
        if reason != "":
            embed.add_field(name="You're here because...", value=reason)
        msg = ("You'll be here for " + timer.get_timestr(time, False) + "!\n\n"
               + "That's " + timer.get_time_offset(time).strftime("%m/%d/%Y, %H:%M:%S") + "! Enjoy!")
        embed.add_field(name="Your sentence...", value=msg, inline=False)
        await brazil_channel.send(embed=embed)

    # Remove a member from Brazil and inform others in #dababy and #brazil
    async def remove_brazil(self, ctx, member):
        brazil_role = await self.get_brazil_role(ctx)
        if brazil_role in member.roles:
            await member.remove_roles(brazil_role)
            await ctx.send(member.display_name + " has been freed from Brazil!")

    # Creates the embed for role info
    # Return: Embed
    @staticmethod
    async def create_role_embed(role):
        mems = ""
        for mem in role.members[:-1]:
            mems += mem.mention + ", "
        mems += role.members[-1].mention
        embed = discord.Embed(color=role.color, title="Role Info", description=role.mention)
        embed.add_field(name="Date Created", value=role.created_at.strftime("%m/%d/%Y"))
        embed.add_field(name="Color", value=str(role.color))
        embed.add_field(name="Members: "+str(len(role.members)), value=mems, inline=False)
        return embed

    # Displays a list of all roles that may be added/removed
    async def rolelist(self, ctx):
        role_list = await self.get_auto_roles(ctx)
        role_str = ""
        mem_count_str = ""
        for role in role_list:
            role_str += role.mention + "\n"
            mem_count_str += str(len(role.members)) + "\n"
        embed = discord.Embed(color=ctx.me.color, title="Role List")
        embed.add_field(name="Role", value=role_str)
        embed.add_field(name="Members", value=mem_count_str)
        embed.set_footer(text="Use /role <role> to add/remove a role.")
        await ctx.respond(embed=embed)

    #######################
    #       COMMANDS      #
    #######################

    # View for /role buttons
    class RoleView(discord.ui.View):
        def __init__(self, role, allowed_roles):
            super().__init__()
            self.role = role
            self.message = None
            if role not in allowed_roles:
                self.clear_items()
                self.add_item(discord.ui.Button(label="This role cannot be added using the bot.", disabled=True, emoji="❌"))
                self.stop()

        async def on_timeout(self):
            self.clear_items()
            self.add_item(discord.ui.Button(label="Timed out! Use /role to get or remove this role.", disabled=True, emoji="⏰"))
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

    # Displays info about a role and the buttons to do it
    @commands.slash_command(guild_ids = [730196305124655176])
    async def role(self, ctx,
        role: discord.Option(str, "Role to view info about", required = False, default = "")
    ):
        """Get info on a role and add/remove that role. Leave blank to see a list of roles."""
        if role == "":
            await self.rolelist(ctx)
            return
        converterplus = self.bot.get_cog("ConverterPlus")
        rol = await converterplus.lookup_role(ctx, role)
        embed = await self.create_role_embed(rol)
        view = self.RoleView(rol, await self.get_auto_roles(ctx))
        intr: discord.Interaction = await ctx.respond(embed=embed, view=view)
        view.message = await intr.original_message()

    # Gives user the Brazil role for some time (in seconds)
    @commands.slash_command(guild_ids = [730196305124655176])
    @discord.permissions.has_role("Admin")
    async def brazil(self, ctx,
        target: discord.Option(str, "Server member to send to Brazil"),
        time: discord.Option(float, "How long to keep the member in Brazil (in seconds)", required = False, default = 60),
        reason: discord.Option(str, "Reason for sending member to Brazil", required = False, default = "")
    ):
        """Send a server member to Brazil for some time."""
        # Find member and check if they're already in Brazil
        converterplus = self.bot.get_cog("ConverterPlus")
        member = await converterplus.lookup_member(ctx, target)
        brazil_role = await converterplus.lookup_role(ctx, "Brazil")
        if brazil_role in member.roles:
            if member.id in self.brazil_times:
                msg = member.display_name + " has " + timer.get_time_until(self.brazil_times[member.id]) + " left in Brazil."
                await ctx.respond(msg)
            else:
                msg = member.display_name + " is in Brazil but shouldn't be! I'll just..."
                await ctx.respond(msg)
                await self.remove_brazil(ctx, member)
            return
        
        # Send user to Brazil
        await self.send_brazil(ctx, member, reason, time)
        self.brazil_times[member.id] = timer.get_time_offset(time)
        # Wait for time, then release automatically
        await asyncio.sleep(time)
        await self.remove_brazil(ctx, member)

def setup(bot):
    bot.add_cog(Roles(bot))