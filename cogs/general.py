import asyncio
import random
import datetime
import discord
from discord.ext import commands
from lyricsgenius import Genius

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_loading_messages = False

    #######################
    #  HELPER FUNCTIONS   #
    #######################

    # Get the bot phrases using Genius
    # Return: List[str]
    async def init_phrases(self, ctx):
        msg = await ctx.send("I'm thinkin! (Loading phrases...)")
        self.is_loading_messages = True
        async with ctx.channel.typing():
            print("Initializaing phrases...")
            genius = Genius("OVZjDThy2v_vmKZ2DrtBSDBPXFQQ09vCEaL5bp-2AeFAXO0h_Hlg-qUfiiugrT67")
            songs = genius.search_artist_songs(search_term="DaBaby", artist_id=1162342, per_page=30)["songs"]
            phrases_list = []
            print("\tSuccessfully retrieved songs...")
            for song in songs:
                lyrics = genius.lyrics(song["id"], remove_section_headers = True)
                temp_list = lyrics.split("\n")
                for temp in temp_list:
                    if (temp != "") and (temp.find("\u200a") == -1) and (temp.find("\u205f") == -1) and (temp.find("\u2005") == -1):
                        phrases_list.append(temp)
            phrases_list.append("动态网自由门 天安門 天安门 法輪功 李洪志 Free Tibet 六四天安門事件 The Tiananmen Square protests of 1989 天安門大屠殺 The Tiananmen Square Massacre 反右派鬥爭")
            phrases_list.append("I hate the antichrist")
        print("Done!")
        await msg.delete()
        self.is_loading_messages = False
        return phrases_list

    # Get every message from up to 2 weeks ago
    # Return: List[Message]
    async def get_message_cache(self, ctx):
        msg = await ctx.send("Lemme look! (Fetching messages...)")
        async with ctx.channel.typing():
            message_cache = []
            for channel in ctx.guild.text_channels:
                perm = channel.permissions_for(ctx.me)
                if perm.read_message_history == True and perm.read_messages == True:
                    after = datetime.datetime.today() - datetime.timedelta(days=14)
                    history = await channel.history(after=after).flatten()
                    for message in history:
                        message_cache.append(message)
        await msg.delete()
        return message_cache


    # Get the number of messages a member recently spent across all visible channels
    # Return: int
    async def get_message_density(self, ctx, member: discord.Member):
        count = 0
        total = 0
        message_cache = await self.get_message_cache(ctx)
        for message in message_cache:
            total += 1
            if message.author == member:
                count += 1
        return count/total
        

    # Get the list of online members for the guild to which the context belongs
    # Return: List[Member]
    async def get_online_members(self, ctx):
        online_members = []
        for mem in ctx.guild.members:
            if mem.status != discord.Status.offline:
                online_members.append(mem)
        return online_members

    # Get the pog value for a particular member, then attempt to swap it
    # Return: bool
    async def get_pog(self, member: discord.Member):
        d = self.bot.pogs
        if member.id not in d:
            d[member.id] = random.choice([True,False])
        if random.choice(range(1,100)) <= 25:
            d[member.id] = not d[member.id]
        return d[member.id]

    
    #######################
    #       COMMANDS      #
    #######################

    # Sends "pong!"; useful for testing connection
    @commands.command(help = "Simply replies \"pong!\"")
    async def ping(self, ctx):
        await ctx.send("pong!")

    
    # Sends a random dababy line
    @commands.command(aliases = ["d"], help = "Sends a random DaBaby phrase.")
    async def dababy(self, ctx):
        while self.is_loading_messages:
            await asyncio.sleep(1)
        if not self.bot.phrases:
            self.bot.phrases = await self.init_phrases(ctx)
        await ctx.send(random.choice(self.bot.phrases))


    # Sends "Run" n<=5 times
    @commands.command(help = "Prompts you to run up to 5 times.")
    async def run(self, ctx, times: int = 1):
        if times > 5 or times < 1:
            await ctx.message.add_reaction("\N{CROSS MARK}")
        else:
            for i in range(times):
                await ctx.send("Run.")
                await asyncio.sleep(1-i/5)


    # States that a random member is suspicious, slightly weighted toward Dante
    @commands.command(help = "States that a random member is suspicious.")
    async def sus(self, ctx):
        members = await self.get_online_members(ctx)
        dante = ctx.guild.get_member(203300119557308417)
        if dante in members:
            members.append(dante)
            members.append(dante)
            members.append(dante)
        msg = "Ayo! **" + random.choice(members).display_name + "** is sus!"
        await ctx.send(content=msg, file=discord.File("resources/JermaSus.jpg"))


    # States whether a given member is poggers
    @commands.command(help = "States whether a given member is poggers. Type \"me\" to test yourself.")
    async def pog(self, ctx, *, target: str):
        converterplus = self.bot.get_cog("ConverterPlus")
        member = await converterplus.lookup_member(ctx, target)
        is_pog = await self.get_pog(member)
        if is_pog:
            await ctx.send(member.display_name + " is **pog!** Let's go!!!")
        else: await ctx.send(member.display_name + " is **not pog!** That's disgusting!!!")


    # Displays info about a particular member
    @commands.command(help = "Displays info about a particular server member. Type \"me\" to get your own.")
    async def stats(self, ctx, *, target: str):
        async with ctx.channel.typing():
            converterplus = self.bot.get_cog("ConverterPlus")
            member = await converterplus.lookup_member(ctx, target)
            msg_density = await self.get_message_density(ctx, member)
            embed = discord.Embed(color = member.top_role.color, title=(member.name+"#"+str(member.discriminator)))
            embed.set_image(url=member.avatar_url_as(format=None, static_format='webp', size=128))
            embed.add_field(name="Top Role", value=member.top_role.name)
            embed.add_field(name="Message Density", value=(str(round(msg_density*100, 2))+"%"))
            embed.set_footer(text="ID: "+str(member.id))
            await ctx.send(embed=embed)        

    
def setup(bot):
    bot.add_cog(General(bot))