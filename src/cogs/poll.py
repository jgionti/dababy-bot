import discord
from discord.ext import commands

from src.constants import GUILD_IDS

#####################
#        poll       #
#####################
# Generate polls in a single command
# No timing or checking is done right now

class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _create_poll_embed(self, author: discord.Member, q: str, ops, reactions) -> discord.Embed:
        desc = f"{q}\n\n"
        for i in range(0, len(ops)):
            desc += f"{reactions[i]} {ops[i]}\n"
        embed = discord.Embed(color=author.top_role.color, title=f"{author.display_name} calls a poll!", description=desc)
        embed.set_thumbnail(url = author.avatar.url)
        return embed

    # Use reactions to host a poll; currently untimed
    @commands.slash_command(guild_ids = GUILD_IDS)
    async def poll( self, ctx,
        question: discord.Option(str, "Question to ask"),
        op1 : discord.Option(str, "Option 1", required = False, default = ""),
        op2 : discord.Option(str, "Option 2", required = False, default = ""),
        op3 : discord.Option(str, "Option 3", required = False, default = ""),
        op4 : discord.Option(str, "Option 4", required = False, default = ""),
        op5 : discord.Option(str, "Option 5", required = False, default = ""),
        op6 : discord.Option(str, "Option 6", required = False, default = ""),
        op7 : discord.Option(str, "Option 7", required = False, default = ""),
        op8 : discord.Option(str, "Option 8", required = False, default = ""),
    ):
        """Ask the group a question and get feedback. Requires 2+ options."""
        args = [op1, op2, op3, op4, op5, op6, op7, op8]
        ops = []
        for op in args:
            if (op != ""):
                ops.append(op)

        reactions = []
        if len(ops) == 0:
            ops = ["Yes", "No"]
            reactions = ["✅", "❌"]
        elif len(ops) >= 2:
            reactions = ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭"]
        else:
            await ctx.respond("👎 Poll must have at least 2 options!", ephemeral=True)
            return

        embed = self._create_poll_embed(ctx.author, question, ops, reactions)
        intr: discord.Interaction = await ctx.respond(embed=embed)
        msg = await intr.original_message()
        for i in range(0, len(ops)):
            await msg.add_reaction(reactions[i])
    

def setup(bot):
    bot.add_cog(Poll(bot))
