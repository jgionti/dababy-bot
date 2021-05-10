import asyncio
import random
import datetime
import discord
from discord.ext import commands
from lyricsgenius import Genius

#####################
#      general      #
#####################
# Main functionalities
# Interactions mainly through text

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot        
        self.has_persona = False
        self.persona_id = 0
        

    #######################
    #  HELPER FUNCTIONS   #
    #######################

    # Get the bot phrases using Genius
    # Return: List[str]
    async def init_phrases(self, ctx):
        msg = await ctx.send("I'm thinkin! (Loading phrases...)")
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
        return phrases_list

    # Get every message from up to 2 weeks ago
    # Return: List[Message]
    async def get_message_cache(self, ctx, days: int=14):
        async with ctx.channel.typing():
            message_cache = []
            for channel in ctx.guild.text_channels:
                perm = channel.permissions_for(ctx.me)
                if perm.read_message_history == True and perm.read_messages == True:
                    after = datetime.datetime.today() - datetime.timedelta(days=days)
                    history = await channel.history(after=after).flatten()
                    for message in history:
                        message_cache.append(message)
        return message_cache

    # Get the number of messages a member recently sent across all visible channels
    # Return: (int, int) in the form (count, total)
    async def get_message_tuple(self, ctx, member: discord.Member):
        count = 0
        total = 0
        msg = await ctx.send("Lemme look! (Fetching messages...)")
        message_cache = await self.get_message_cache(ctx)
        await msg.delete()
        for message in message_cache:
            total += 1
            if message.author == member:
                count += 1
        return (count, total)
        
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

    # Sends "pong!"; useful for testing connection
    @commands.command(help = "Simply replies \"pong!\"")
    async def ping(self, ctx):
        await ctx.send("pong!")

    
    # Sends a random dababy line
    @commands.command(aliases = ["d"], help = "Sends a random DaBaby phrase.")
    @commands.max_concurrency(1, per=commands.BucketType.guild, wait=True)
    async def dababy(self, ctx):
        if self.has_persona:
            await ctx.send(random.choice(self.bot.persona))
            return
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


    # States that a random online member is suspicious, slightly weighted toward Dante
    @commands.command(help = "States that a random member is suspicious.")
    async def sus(self, ctx):
        members = await self.get_online_members(ctx)
        dante = ctx.guild.get_member(203300119557308417)
        if dante in members:
            members.append(dante)
            members.append(dante)
            members.append(dante)
        num = random.choice(range(1,1000))
        name = random.choice(members).display_name
        if num <= 10:
            # Super sus
            msg = "Yo, emergency meeting! **" + name + "** is **super sus!**"
            fil = discord.File("resources/SuperSus.jpg")
        elif num == 11:
            # Mega sus
            msg = "Uh, oh no... this can't be right...\n**" + name + "** is **MEGA SUS!**"
            fil = discord.File("resources/MegaSus.mp4")
        else:
            # Normal sus
            msg = "Ayo! **" + name + "** is sus!"
            fil = discord.File("resources/JermaSus.jpg")
        await ctx.send(content=msg, file=fil)

    # Like the sus command, but forces a super sus, not weighted toward Dante this time
    # 24 hour cooldown
    @commands.command(help = "States that a random member is super suspicious. 24 hour cooldown.")
    @commands.cooldown(1, 86400, commands.BucketType.guild)
    async def supersus(self, ctx):
        members = await self.get_online_members(ctx)
        name = random.choice(members).display_name
        msg = "Yo, emergency meeting! **" + name + "** is **super sus!**"
        fil = discord.File("resources/SuperSus.jpg")
        await ctx.send(content=msg, file=fil)


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
            msg_tuple = await self.get_message_tuple(ctx, member)
            msg_density = msg_tuple[0]/msg_tuple[1]
            role_str = await self.get_role_string(member)
            embed = discord.Embed(color = member.top_role.color, title=(member.name+"#"+str(member.discriminator)))
            embed.set_image(url=member.avatar_url_as(format=None, static_format='webp', size=128))
            embed.add_field(name="Mention", value=member.mention)
            embed.add_field(name="Recent Messages", value=(str(msg_tuple[0])))
            embed.add_field(name="Message Density", value=(str(round(msg_density*100, 2))+"%"))
            embed.add_field(name="Roles", value=role_str, inline=False)
            embed.set_footer(text="ID: "+str(member.id))
            await ctx.send(embed=embed)


    # Changes pool of messages the bot pulls from in $dababy
    # 30 second cooldown
    @commands.command(aliases = ["p"], help = "Changes the pool of messages used in $dababy to those of a particular server member. 30 second cooldown. Use with no args to reset.")
    @commands.cooldown(1, 30, commands.BucketType.guild)
    async def persona(self, ctx, *, target: str=""):
        if target != "":
            converterplus = self.bot.get_cog("ConverterPlus")
            member = await converterplus.lookup_member(ctx, target)
        if target == "" or member == ctx.guild.me:
            self.has_persona = False
            await ctx.guild.me.edit(nick="DaBaby")
            await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")
            return

        if member.id == self.persona_id:
            await ctx.message.add_reaction("\N{CROSS MARK}")
            return

        msg = await ctx.send("Yeah, I can do that! (Loading messages...)")
        message_cache = await self.get_message_cache(ctx, 31)
        phrases_list = []
        for message in message_cache:
            if (message.author == member) and (message.content != "") and not message.mentions:
                phrases_list.append(message.content)
        
        self.bot.persona = phrases_list
        self.has_persona = True
        await ctx.guild.me.edit(nick=("DaBaby \"" + member.display_name + "\""))
        await msg.delete()
        await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")

    

def setup(bot):
    bot.add_cog(General(bot))