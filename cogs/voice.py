import asyncio
import time
import youtube_dl
import discord
import random
from discord.ext import commands
from cogs import timer

#####################
#       voice       #
#####################
# All voice functions
# Includes Youtube radio functionality

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.q = [] # music queue
        self.np = None

    # Disconnect on error
    @commands.Cog.listener()
    async def on_command_error(self, ctx):
        await self.dc(ctx)

    #######################
    #  HELPER FUNCTIONS   #
    #######################

    # Joins the author's vc if not already in it
    # Return: None
    async def join(self, ctx):
        # Check if bot is connected to any vc
        if not ctx.voice_client:
            await ctx.author.voice.channel.connect(reconnect=False)
        # Check if bot is called to different vc
        elif ctx.me.voice.channel.id != ctx.author.voice.channel.id:
            await ctx.voice_client.move_to(ctx.author.voice.channel)

    # Automatically plays the next song and adjusts the queue accordingly
    # Returns: None
    def play_next(self, ctx: commands.Context):
        self.np = None
        if len(self.q) > 0:
            info = self.q.pop(0)
            source = info['formats'][0]['url']
            ctx.voice_client.play(discord.FFmpegPCMAudio(source), after=lambda e: self.play_next(ctx))
            self.np = info
        else:
            # Disconnect after some time of inactivity
            for i in range(30):
                time.sleep(1)
                if ctx.voice_client.is_playing():
                    return
            if ctx.voice_client is not None and not ctx.voice_client.is_playing():
                num = random.choice(range(1,100))
                if num > 1: 
                    file = "resources/lets-go.mp3"
                else: file = "resources/among-us.mp3"
                ctx.voice_client.play(discord.FFmpegPCMAudio(file))
                time.sleep(3.2)
                asyncio.run_coroutine_threadsafe(self.dc(ctx), self.bot.loop)

    # Disconnects from a voice channel (returns whether successful)
    # Return: bool
    async def dc(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_connected:
            await ctx.voice_client.disconnect()
            return True
        return False

    # Generates a Discord-formatted hyperlink for a particular song
    # Return: str
    def hyperlink(self, song_info):
        return "["+song_info["title"]+"]" + "("+song_info["webpage_url"]+")"


    #######################
    #       COMMANDS      #
    #######################

    # Queues up and plays a YouTube video (by URL or search)
    @commands.command(aliases = ["p"], help = "Add a video to the queue. Supports URL or Youtube search.")
    async def play(self, ctx, *, arg: str):
        # Initial check: only join if author is in a vc
        if ctx.author.voice == None:
            await ctx.send("Join a voice channel first, bozo! \N{CLOWN FACE}")
            return

        # Begin search
        await ctx.send("\N{RIGHT-POINTING MAGNIFYING GLASS} **Searching:** `"+arg+"`")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],}
        ytdl = youtube_dl.YoutubeDL(ydl_opts)
        # Try any url first
        try:
            info = ytdl.extract_info(arg, download=False)
        # Search YouTube manually if not
        except:
            info = ytdl.extract_info("ytsearch:"+arg, download=False)["entries"][0]

        await self.join(ctx)
        info["requested_by"] = ctx.author

        if ctx.voice_client.is_playing():
            self.q.append(info)
            await ctx.send("**Queued up:** `"+info["title"]+"`")
        else:
            source = info['formats'][0]['url']
            ctx.voice_client.play(discord.FFmpegPCMAudio(source), after=lambda e: self.play_next(ctx))
            await ctx.send("**Now playing:** \N{MUSICAL NOTE} `"+info["title"]+"`")
            self.np = info


    # Sends info about the songs in the queue
    @commands.command(aliases = ["q"], help = "Displays info about the songs in the queue.")
    async def queue(self, ctx):
        if self.np is not None:
            req = self.np["requested_by"]
            queue = "__Now playing__\n"+self.hyperlink(self.np) + \
                "\n`(" + timer.get_timestr(self.np["duration"]) + ") Requested by "+ req.name+"#"+req.discriminator+ "`\n\n"
            if len(self.q) > 0:
                queue += "__Coming up__\n"
                index = 1
                for song in self.q:
                    req = song["requested_by"]
                    queue += "`"+str(index)+".` " + self.hyperlink(song) + \
                        "\n`(" + timer.get_timestr(song["duration"]) + ") Requested by "+ req.name+"#"+req.discriminator+ "`\n\n"
                    index += 1
                queue += "**There are "+str(index-1)+" songs in queue.**"
            embed = discord.Embed(title = "Queue for "+ctx.guild.name,
                description = queue,
                color = ctx.me.color)
            await ctx.send(embed=embed)
        else:
            await ctx.send("I'm not playing anything right now, bozo! \N{CLOWN FACE}")

    # Clears the queue
    @commands.command(aliases = ["c"], help = "Clears the queue.")
    async def clear(self, ctx):
        if len(self.q) > 0:
            self.q = []
            await ctx.send("**No! More! Queue!** \N{COLLISION SYMBOL} (Queue cleared)")
        else:
            await ctx.send("There is no queue, bozo! \N{CLOWN FACE}")
    
    # Sends info about the song currently playing
    @commands.command(aliases = ["np"], help = "Displays info about the currently playing song.")
    async def nowplaying(self, ctx):
        if self.np is not None:
            embed = discord.Embed(title = "Now Playing",
                description = self.hyperlink(self.np),
                color = self.np["requested_by"].top_role.color)
            embed.set_footer(text="Requested by: "+self.np["requested_by"].name+"#"+self.np["requested_by"].discriminator)
            embed.set_thumbnail(url=self.np["thumbnail"])
            await ctx.send(embed=embed)
        elif ctx.voice_client.is_playing():
            await ctx.send("I don't know what I'm playing right now! \N{CLOWN FACE}")
        else:
            await ctx.send("I'm not playing anything right now, bozo! \N{CLOWN FACE}")

    # Disconnects from current vc if applicable
    @commands.command(aliases = ["dc", "die"], help = "Disconnect from the current voice channel.")
    async def disconnect(self, ctx):
        dc_successful = await self.dc(ctx)
        if dc_successful:
            await ctx.send("Disconnected \N{WHITE HEAVY CHECK MARK}")
        else:
            await ctx.send("I'm not in a voice channel right now, bozo! \N{CLOWN FACE}")

    # Skips to next song in queue
    @commands.command(aliases = ["s","fs"], help = "Skip to the next song in the queue.")
    async def skip(self, ctx):
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE} **Skipped!**")
        else:
            await ctx.send("I'm not playing anything right now, bozo! \N{CLOWN FACE}")

    # Pause the current song being played
    @commands.command(help = "Pause the song currently being played.")
    async def pause(self, ctx):
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("\N{DOUBLE VERTICAL BAR} **Paused!**")

    # Resume the current song being paused
    @commands.command(help = "Resume the song currently being paused.")
    async def resume(self, ctx):
        if ctx.voice_client.is_paused:
            ctx.voice_client.resume()
            await ctx.send("\N{BLACK RIGHT-POINTING TRIANGLE} **Resuming!**")


def setup(bot):
    bot.add_cog(Voice(bot))