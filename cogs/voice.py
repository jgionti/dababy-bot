import asyncio
import time

import discord
import youtube_dl
from discord.ext import commands
from lib import autocomplete, timer, chance

#####################
#       voice       #
#####################
# All voice functions
# Includes Youtube music functionality

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.q = [] # music queue
        self.np = None

        self.vc_log = []

    # Disconnect on error
    @commands.Cog.listener()
    async def on_application_command_error(self, ctx):
        await self.disconnect(ctx)

    # Save info on join/leave
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        await self.update_vc_log(member, before, after)

    #######################
    #  HELPER FUNCTIONS   #
    #######################

    # Joins the author's vc if not already in it
    # Return: None
    async def join(self, ctx: commands.Context):
        # Check if bot is connected to any vc
        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()
        # Check if bot is called to different vc
        elif ctx.me.voice.channel.id != ctx.author.voice.channel.id:
            await ctx.voice_client.move_to(ctx.author.voice.channel)

    # Disconnects from a voice channel (returns whether successful)
    # Return: bool
    async def disconnect(self, ctx: commands.Context):
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

    # Creates the embed for queue info
    # Return: Embed
    def create_queue_embed(self, ctx):
        req = self.np["requested_by"]
        queue = "__Now playing__\n"+self.hyperlink(self.np) + \
            "\n`(" + timer.get_timestampstr(self.np["duration"]) + ") Requested by "+ req.name+"#"+req.discriminator+ "`\n\n"
        if len(self.q) > 0:
            queue += "__Coming up__\n"
            index = 1
            for song in self.q:
                req = song["requested_by"]
                queue += "`"+str(index)+".` " + self.hyperlink(song) + \
                    "\n`(" + timer.get_timestampstr(song["duration"]) + ") Requested by "+ req.name+"#"+req.discriminator+ "`\n\n"
                index += 1
            queue += "**There are "+str(index-1)+" songs in queue.**"
        embed = discord.Embed(title = "Queue for "+ctx.guild.name,
            description = queue,
            color = ctx.me.color)
        embed.set_thumbnail(url=self.np["thumbnail"])
        return embed

    # Create embed for current song info
    # Return: Embed
    def create_song_embed(self, ctx, info, prefix: str):
        req = info["requested_by"]
        dur = timer.get_timestampstr(info["duration"]) if "duration" in info.keys() else ""
        np = f"{self.hyperlink(info)}\n`" + \
            (f"({dur}) " if dur != "" else "") + \
            f"Requested by "+ req.name+"#"+req.discriminator+ "`\n\n"
        embed = discord.Embed(title = prefix+":",
            description = np,
            color = ctx.me.color)
        url = info["thumbnail"] if "thumbnail" in info.keys() else self.bot.user.avatar.url
        embed.set_thumbnail(url=url)
        return embed

    # Generates a Discord-formatted hyperlink for a particular song
    # Return: str
    def hyperlink(self, song_info):
        return "["+song_info["title"]+"]" + "("+song_info["webpage_url"]+")"

    # Update VoiceState changelog for /whojust
    async def update_vc_log(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        action = ""
        channel = None

        # Check for join
        if after.channel and (not before.channel or before.channel.id != after.channel.id):
            action = "joined"
            channel = after.channel
        # Check for leave
        elif before.channel and (not after.channel or after.channel.id != before.channel.id):
            action = "left"
            channel = before.channel
        
        if action != "":
            log_data = {"member" : member.mention, "action" : action, "channel" : channel.name, "time" : time.time()}
            self.vc_log.insert(0, log_data)
            if (len(self.vc_log) > 5): self.vc_log.pop()

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
            for i in range(90):
                time.sleep(1)
                if ctx.voice_client is not None and ctx.voice_client.is_playing():
                    return
            if ctx.voice_client is not None and not ctx.voice_client.is_playing():
                if chance.chance(1):
                    file = "resources/among-us.mp3"
                else: file = "resources/lets-go.mp3"
                ctx.voice_client.play(discord.FFmpegPCMAudio(file))
                time.sleep(3.2)
                asyncio.run_coroutine_threadsafe(self.disconnect(ctx), self.bot.loop)

    #######################
    #       COMMANDS      #
    #######################

    # Queues up and plays a YouTube video (by URL or search)
    @commands.slash_command(guild_ids = [730196305124655176])
    async def play(self, ctx: discord.ApplicationContext,
        url: discord.Option(str, "URL or YouTube search term of the audio to queue up and play.", autocomplete = autocomplete.get_yt)
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

        prefix = ""
        if ctx.voice_client.is_playing():
            self.q.append(info)
            prefix = "Queued Up"
        else:
            source = info['formats'][0]['url']
            ctx.voice_client.play(discord.FFmpegPCMAudio(source), after=lambda e: self.play_next(ctx))
            self.np = info
            prefix = "Now Playing"
        embed = self.create_song_embed(ctx, info, prefix)
        await intr.edit_original_message(content="", embed=embed)

    # Sends info about the songs in the queue
    @commands.slash_command(guild_ids = [730196305124655176])
    async def queue(self, ctx):
        """Displays info about the songs in the queue."""
        if self.np is not None:
            intr: discord.Interaction = await ctx.respond("Generating queue...")
            embed = self.create_queue_embed(ctx)
            #view = self.QueueView(ctx)
            await intr.edit_original_message(content="", embed=embed)
        else:
            await ctx.respond("I'm not playing anything right now, bozo! \N{CLOWN FACE}")

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

    # Send who just joined or left the vc
    @commands.slash_command(guild_ids = [730196305124655176])
    async def whojust(self, ctx):
        """Find out who recently joined or left the voice channel."""
        if len(self.vc_log) == 0:
            await ctx.respond("Nobody's done anything recently, bozo! 🤡", ephemeral=True)
            return

        msg = "Here's the scoop:"
        for data in self.vc_log:
            timestr = timer.get_timestr(int(time.time() - data["time"]))
            msg += f"\n{data['member']} {data['action']} [{data['channel']}] {timestr} ago."
        await ctx.respond(msg, ephemeral=True)

def setup(bot):
    bot.add_cog(Voice(bot))
