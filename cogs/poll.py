import discord
from discord.ext import commands

class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #######################
    #  HELPER FUNCTIONS   #
    #######################

    # Constructs/sends a poll based on given instructions for (time) minutes, returning 1-6
    # Return: int
    async def send_poll(self, ctx, time:float, input_str:str):
        await ctx.message.delete()
        # 1. Deconstruct string and determine poll type
        poll_list = input_str.split()
        length = len(poll_list)
        if (length < 1) or (length == 2):  # Invalid poll
            raise commands.MissingRequiredArgument("Too few args for poll!")
        if (length == 1):  # Y/N poll
            poll_list.append("\N{WHITE HEAVY CHECK MARK} Yes")
            poll_list.append("\N{CROSS MARK} No")
        else:  #1-6 poll
            if (length >= 2): poll_list[1] = "\N{DIGIT ONE}" + poll_list[1]
            if (length >= 3): poll_list[2] = "\N{DIGIT TWO}" + poll_list[2]
            if (length >= 4): poll_list[3] = "\N{DIGIT THREE}" + poll_list[3]
            if (length >= 5): poll_list[4] = "\N{DIGIT FOUR}" + poll_list[4]
            if (length >= 6): poll_list[5] = "\N{DIGIT FIVE}" + poll_list[5]
            if (length >= 7): poll_list[6] = "\N{DIGIT SIX}" + poll_list[6]
        # 2. Construct embed using poll_list
        embed = discord.Embed(color=ctx.author.top_role.color, title=(ctx.author.name+" wants to call a poll!"))
        embed.description = poll_list[0]

        embed.set_thumbnail(url=ctx.author.avatar_url)
        # 3. Send embed and send initial reactions
        await ctx.send(embed=embed)
        # 4. Wait for *time* minutes
        # 5. Use dictionary to sum points
        d = {}
        # 6. Return the winning number (Y=1, N=2 for Y/N)
        return 1

    #######################
    #       COMMANDS      #
    #######################

    # Sends a poll based on time input string, then states the result
    @commands.command(aliases = ["p"], help = "")
    async def test(self, ctx, time:float=5.0, *, input_str:str=""):
        await self.send_poll(ctx, time, input_str)

    # to do: endpoll()
    # ends poll early
    

def setup(bot):
    bot.add_cog(Poll(bot))