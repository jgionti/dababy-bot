import asyncio
import discord
from discord.ext import commands

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #######################
    #  HELPER FUNCTIONS   #
    #######################

    # Get the function to help sort get_gaming_roles() with
    # Return: str
    def role_sort(self, role: discord.Role):
        return role.name

    # Get the roles the bot should handle
    # Return: List[Role]
    async def get_gaming_roles(self, ctx):
        brazil_role = ctx.guild.get_role(748221820456402965)
        gaming_roles = []
        for role in ctx.guild.roles:    # 7482... is Brazil role
            if role.position < brazil_role.position and role.position > 0:
                gaming_roles.append(role)
        gaming_roles.reverse()
        gaming_roles.sort(key=self.role_sort)
        return gaming_roles
        

    #######################
    #       COMMANDS      #
    #######################

    # Adds a role to the user who requested it
    # Uses reactions to determine whether successful
    @commands.command(aliases = ["ar", "arole"], help = "Adds a gaming role to your account.")
    async def addrole(self, ctx, *, target_role: str):
        converterplus = self.bot.get_cog("ConverterPlus")
        role = await converterplus.lookup_role(ctx, target_role)
        gaming_roles = await self.get_gaming_roles(ctx)
        if role in ctx.author.roles or role not in gaming_roles:
            await ctx.message.add_reaction("\N{CROSS MARK}")
        else:
            await ctx.author.add_roles(role)
            await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")

    # Removes a role from the user who requested it
    # Uses reactions to determine whether successful
    @commands.command(aliases = ["rr", "rrole"], help = "Removes a gaming role from your account.")
    async def removerole(self, ctx, *, target_role: str):
        converterplus = self.bot.get_cog("ConverterPlus")
        role = await converterplus.lookup_role(ctx, target_role)
        gaming_roles = await self.get_gaming_roles(ctx)
        if role in ctx.author.roles and role in gaming_roles:
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

    # Displays a list of all gaming roles that may be added/removed
    @commands.command(aliases = ["rl", "rlist"], help = "Displays all gaming roles.")
    async def rolelist(self, ctx):
        role_list = await self.get_gaming_roles(ctx)
        role_str = ""
        mem_count_str = ""
        for role in role_list:
            role_str += role.mention + "\n"
            mem_count_str += str(len(role.members)) + "\n"
        embed = discord.Embed(color=ctx.me.color, title="Role List")
        embed.add_field(name="Role", value=role_str)
        embed.add_field(name="Members", value=mem_count_str)
        embed.set_footer(text="Use $addrole <role> to add a gaming role\n"\
            +"Use $removerole <role> to remove a gaming role\n"\
            +"Use $roleinfo <role> for more info on a role")
        await ctx.send(embed=embed)


    # Gives user the Brazil role for some time
    # Admin only, of course
    @commands.command(aliases = ["b", "br", "brazil"], help = "Admin only. Sends a member to Brazil for a set amount of time.")
    @commands.has_permissions(administrator=True)
    async def brazilfor(self, ctx, time: float, *, target: str):
        converterplus = self.bot.get_cog("ConverterPlus")
        member = await converterplus.lookup_member(ctx, target)
        brazil_role = ctx.guild.get_role(748221820456402965)
        if brazil_role in member.roles:
            await ctx.message.add_reaction("\N{CROSS MARK}")
        else:
            await ctx.send("Get the boot. " + member.name + " is going to Brazil!")
            await member.add_roles(brazil_role)
            await asyncio.sleep(time)
            if brazil_role in member.roles:
                await member.remove_roles(brazil_role)
                await ctx.send(member.name + " has been freed from Brazil!")

def setup(bot):
    bot.add_cog(Roles(bot))