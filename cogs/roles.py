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
    async def send_brazil(self, ctx, member, reason, time):
        brazil_role = await self.get_brazil_role(ctx)
        brazil_channel = await self.get_brazil_channel(ctx)
        await ctx.send("Get the boot. **" + member.display_name + "** is going to Brazil!")
        await member.add_roles(brazil_role)
        msg = "**Welcome to Brazil, " + member.display_name + "!**\n"\
            + (("__You're here because__: " + reason + '\n') if reason != "" else "")\
            + "You'll be here for " + str(time) + " seconds! Enjoy!"
        await brazil_channel.send(msg)

    # Remove a member from Brazil and inform others in #dababy and #brazil
    async def remove_brazil(self, ctx, member):
        brazil_role = await self.get_brazil_role(ctx)
        if brazil_role in member.roles:
            await member.remove_roles(brazil_role)
            await ctx.send(member.display_name + " has been freed from Brazil!")

    #######################
    #       COMMANDS      #
    #######################

    # Adds a role to the user who requested it
    # Uses reactions to determine whether successful
    @commands.command(aliases = ["ar", "arole"], help = "Adds a role to your account.")
    async def addrole(self, ctx, *, target_role: str):
        converterplus = self.bot.get_cog("ConverterPlus")
        role = await converterplus.lookup_role(ctx, target_role)
        auto_roles = await self.get_auto_roles(ctx)
        if role in ctx.author.roles or role not in auto_roles:
            await ctx.message.add_reaction("\N{CROSS MARK}")
        else:
            await ctx.author.add_roles(role)
            await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")

    # Removes a role from the user who requested it
    # Uses reactions to determine whether successful
    @commands.command(aliases = ["rr", "rrole"], help = "Removes a role from your account.")
    async def removerole(self, ctx, *, target_role: str):
        converterplus = self.bot.get_cog("ConverterPlus")
        role = await converterplus.lookup_role(ctx, target_role)
        auto_roles = await self.get_auto_roles(ctx)
        if role in ctx.author.roles and role in auto_roles:
            await ctx.author.remove_roles(role)
            await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")
        else:
            await ctx.message.add_reaction("\N{CROSS MARK}")


    # Displays info about a role, similar to user stats
    @commands.command(aliases = ["ri", "rinfo"], help = "Displays info about a particular role.")
    async def roleinfo(self, ctx, *, target_role: str = ""):
        if target_role == "":
            return await self.rolelist(ctx)
        converterplus = self.bot.get_cog("ConverterPlus")
        role = await converterplus.lookup_role(ctx, target_role)
        mems = ""
        for mem in role.members[:-1]:
            mems += mem.name + ", "
        mems += role.members[-1].name
        embed = discord.Embed(color=role.color, title="Role Info", description=role.mention)
        embed.add_field(name="Date Created", value=role.created_at.strftime("%m/%d/%Y"))
        embed.add_field(name="Color", value=str(role.color))
        embed.add_field(name="Members: "+str(len(role.members)), value=mems, inline=False)
        embed.set_footer(text="ID: "+str(role.id))
        await ctx.send(embed=embed)

    # Displays a list of all roles that may be added/removed
    @commands.command(aliases = ["rl", "rlist"], help = "Displays all roles that Dababy can add/remove.")
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
        embed.set_footer(text="Use $addrole <role> to add a role\n"\
            +"Use $removerole <role> to remove a role\n"\
            +"Use $roleinfo <role> for more info on a role")
        await ctx.send(embed=embed)


    # Gives user the Brazil role for some time (in seconds)
    # Admin only, of course
    @commands.command(aliases = ["b"], help = "Admin only. Sends a member to Brazil for a set amount of time (in seconds).")
    @commands.has_permissions(administrator=True)
    async def brazil(self, ctx, target: str, time: float=60, *, reason: str=""):
        # Find member and check if they're already in Brazil
        converterplus = self.bot.get_cog("ConverterPlus")
        member = await converterplus.lookup_member(ctx, target)
        brazil_role = await converterplus.lookup_role(ctx, "Brazil")
        if brazil_role in member.roles:
            if member.id in self.brazil_times:
                msg = member.display_name + " has " + timer.get_time_until(self.brazil_times[member.id]) + " left in Brazil."
                await ctx.send(msg)
            else:
                msg = member.display_name + " is in Brazil but shouldn't be! I'll just..."
                await ctx.send(msg)
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