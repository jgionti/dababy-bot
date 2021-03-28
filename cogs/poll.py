import discord
from discord.ext import commands

class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #######################
    #  HELPER FUNCTIONS   #
    #######################

    # # Constructs/sends a poll based on given instructions for (time) minutes, returning 0-3
    # # Return: int
    # async def send_poll(self, ctx, time:float, input_str:str):
    #     d = {}
    #     await ctx.message.delete()
    #     # Deconstruct string
    #     poll_list = input_str.split()
    #     if (len(poll_list) < 3):
    #         raise MissingRequiredArgument("Too few args!")
    #     if (len(poll_list == 3)):
    #         # To do: special Y/N emojis
    #         # otherwise: 1,2,3,4
    #         # Implement hard cap of 5 entries?
    #     # Construct embed
    #     embed = discord.Embed(color=ctx.author.top_role.color, title=(ctx.author.name))#+" wants to call a poll!"))
    #     embed.description = 
    #     embed.set_thumbnail(url=ctx.author.avatar_url)
    #     # Use dictionary

    #     await ctx.send(embed=embed)
    #     return 1

    #######################
    #       COMMANDS      #
    #######################

    # Sends a poll based on time input string, then states the result
    # @commands.command(aliases = ["p"], help = "")
    # async def test(self, ctx, time:float=5.0, *, input_str:str=""):
    #     await self.send_poll(ctx, time, input_str)
    

def setup(bot):
    bot.add_cog(Poll(bot))