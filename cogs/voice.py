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
    async def on_application_command_error(self, ctx):
        await self.disconnect(ctx)

    #######################
    #  HELPER FUNCTIONS   #
    #######################

    # Joins the author's vc if not already in it
    # Return: None
    async def join(self, ctx):
        # Check if bot is connected to any vc
        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()
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
                if ctx.voice_client is not None and ctx.voice_client.is_playing():
                    return
            if ctx.voice_client is not None and not ctx.voice_client.is_playing():
                num = random.choice(range(1,100))
                if num > 1: 
                    file = "resources/lets-go.mp3"
                else: file = "resources/among-us.mp3"
                ctx.voice_client.play(discord.FFmpegPCMAudio(file))
                time.sleep(3.2)
                asyncio.run_coroutine_threadsafe(self.disconnect(ctx), self.bot.loop)

    # Disconnects from a voice channel (returns whether successful)
    # Return: bool
    async def disconnect(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_connected:
            await ctx.voice_client.disconnect()
            return True
        return False

    # Skip the currently playing audio (returns whether successful)
    # Return: bool
    @staticmethod
    async def _skip(ctx):
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            return True
        return False

    # Generates a Discord-formatted hyperlink for a particular song
    # Return: str
    def hyperlink(self, song_info):
        return "["+song_info["title"]+"]" + "("+song_info["webpage_url"]+")"

    #######################
    #       COMMANDS      #
    #######################

    class QueueView(discord.ui.View):
        def __init__(self, ctx):
            super().__init__()
            self.ctx = ctx

        async def on_timeout(self):
            self.clear_items()
            self.add_item(discord.ui.Button(label="Timed out! Use /queue to bring up radio controls.", disabled=True, emoji="⏰"))

        async def update(self):
            pass
            # TODO: update queue embed

        @discord.ui.button(label="Skip", style=discord.ButtonStyle.green, emoji="⏩")
        async def skip(self, button: discord.ui.Button, interaction: discord.Interaction):
            skipped = await Voice._skip(self.ctx)
            if skipped:
                await interaction.response.send_message("\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE} **Skipped!**")
            else:
                await interaction.response.send_message("I'm not playing anything right now, bozo! \N{CLOWN FACE}")

    # Queues up and plays a YouTube video (by URL or search)
    @commands.slash_command(guild_ids = [730196305124655176])
    async def play(self, ctx,
        url: discord.Option(str, "URL or YouTube search term of the audio to queue up and play.")
    ):
        """Add a video to the queue. Supports URL or YouTube search."""
        # Initial check: only join if author is in a vc
        if ctx.author.voice == None:
            await ctx.respond("Join a voice channel first, bozo! \N{CLOWN FACE}")
            return
        # Begin search
        intr: discord.Interaction = await ctx.respond("\N{RIGHT-POINTING MAGNIFYING GLASS} **Searching:** `"+url+"`")
        
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
            info = ytdl.extract_info(url, download=False)
        # Search YouTube manually if not
        except:
            info = ytdl.extract_info("ytsearch:"+url, download=False)["entries"][0]

        await self.join(ctx)
        info["requested_by"] = ctx.author

        if ctx.voice_client.is_playing():
            self.q.append(info)
            await intr.edit_original_message(content="**Queued up:** `"+info["title"]+"`")
        else:
            source = info['formats'][0]['url']
            ctx.voice_client.play(discord.FFmpegPCMAudio(source), after=lambda e: self.play_next(ctx))
            await intr.edit_original_message(content="**Now playing:** \N{MUSICAL NOTE} `"+info["title"]+"`")
            self.np = info

    # Sends info about the songs in the queue
    #@commands.command(aliases = ["q"], help = "Displays info about the songs in the queue.")
    @commands.slash_command(guild_ids = [730196305124655176])
    async def queue(self, ctx):
        """Displays info about the songs in the queue."""
        if self.np is not None:
            intr: discord.Interaction = await ctx.respond("Generating queue...")
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
            embed.set_thumbnail(url=self.np["thumbnail"])
            view = self.QueueView(ctx)
            await intr.edit_original_message(content="", embed=embed)
        else:
            await ctx.respond("I'm not playing anything right now, bozo! \N{CLOWN FACE}")

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
    @commands.slash_command(guild_ids = [730196305124655176])
    async def dc(self, ctx):
        """Disconnect from the current voice channel."""
        dc_successful = await self.disconnect(ctx)
        if dc_successful:
            await ctx.respond("Disconnected \N{WHITE HEAVY CHECK MARK}")
        else:
            await ctx.respond("I'm not in a voice channel right now, bozo! \N{CLOWN FACE}")

    # Skips to next song in queue
    @commands.slash_command(guild_ids = [730196305124655176])
    async def skip(self, ctx):
        """Skip to the next song in the queue."""
        skipped = await self._skip(ctx)
        if skipped:
            await ctx.respond("\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE} **Skipped!**")
        else:
            await ctx.respond("I'm not playing anything right now, bozo! \N{CLOWN FACE}")

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