import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

from src import autocomplete, converterplus
from src.constants import GUILD_IDS, IS_BETA
from src.dababy_bot import DaBabyBot
from src.database import Database

#####################
#       stats       #
#####################
# Tracks member/server statistics
# Uses database to store/load

class Stats(commands.Cog):

    GOLDEN_REACTION_THRESHOLD = 3 if not IS_BETA else 1
    GOLDEN_MOMENTS_CHANNEL_NAME = "golden-moments"

    def __init__(self, bot: commands.Bot):
        self.bot: DaBabyBot = bot

    def ensure_member_exists(self, id: str):
        if self.bot.db.read(Database.COLLECTION_MEMBERS, id) is None:
            self.bot.db.write(Database.COLLECTION_MEMBERS, id, {})

    @commands.Cog.listener()
    async def on_ready(self):
        """On boot, ensure that all server members are added to the database."""
        for id in GUILD_IDS:
            guild = self.bot.get_guild(id)
            for member in guild.members:
                self.ensure_member_exists(str(member.id))

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """When a member joins, add them to the database."""
        self.ensure_member_exists(str(member.id))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        id = str(message.author.id)
        self.bot.db.add_to_field(Database.COLLECTION_MEMBERS, id, "messageCount", 1)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, raw_reaction: discord.RawReactionActionEvent):
        guild = self.bot.get_guild(raw_reaction.guild_id)
        channel = self.bot.get_channel(raw_reaction.channel_id)
        message = await channel.fetch_message(raw_reaction.message_id)
        reaction = discord.utils.get(
            message.reactions,
            emoji=raw_reaction.emoji.name if raw_reaction.emoji.is_unicode_emoji() else raw_reaction.emoji
        )

        await self.handle_golden_moment(guild, channel, message, reaction)

    # TODO:
    # on_voice_state_update

    async def handle_golden_moment(self, guild: discord.Guild, channel: discord.TextChannel, message: discord.Message, reaction: discord.Reaction):
        golden_moments_channel = discord.utils.get(guild.text_channels, name=self.GOLDEN_MOMENTS_CHANNEL_NAME)
        
        if golden_moments_channel is None or channel.id == golden_moments_channel.id:
            return
        if reaction is None or reaction.count < self.GOLDEN_REACTION_THRESHOLD:
            return

        if self.bot.db.read(Database.COLLECTION_GOLDEN_MOMENTS, str(message.id), {}):
            return

        emoji = reaction.emoji
        emoji_str = (
            f"[{emoji}]({emoji.url})"
            if isinstance(emoji, (discord.Emoji)) and not emoji.is_usable() or isinstance(emoji, (discord.PartialEmoji))
            else emoji
        )
        author_icon = (
            emoji.url
            if isinstance(emoji, (discord.PartialEmoji))
            else message.author.display_avatar.url
        )
        embed_image_url = (
            message.attachments[0].url if message.attachments and message.attachments[0].url else
            message.embeds[0].thumbnail.url if message.embeds and message.embeds[0].thumbnail and message.embeds[0].thumbnail.url else
            message.embeds[0].url if message.embeds and message.embeds[0].url else
            None
        )

        embed = discord.Embed(color=message.author.top_role.color)
        embed.add_field(name="Author", value=message.author.mention)
        embed.add_field(name="Message", value=message.jump_url)
        embed.add_field(name="Emoji", value=f"{reaction.count} {emoji_str}")
        embed.set_author(name="golden moment", icon_url=author_icon)
        embed.set_image(url=embed_image_url)
        if message.content:
            embed.add_field(name="", value=message.content[:1000], inline=False)

        await golden_moments_channel.send(embed=embed)

        self.bot.db.write(Database.COLLECTION_GOLDEN_MOMENTS, str(message.id), {
            "channel_id": str(channel.id),
        })
        self.bot.db.add_to_field(Database.COLLECTION_MEMBERS, str(message.author.id), "golden_moments", 1)

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

    @app_commands.command()
    @app_commands.guilds(*GUILD_IDS)
    @app_commands.describe(
        member="Server member to get info about"
    )
    @app_commands.autocomplete(member=autocomplete.get_members)
    async def info(self, interaction: discord.Interaction, 
        member: Optional[str] = "me"
    ):
        """Displays info about a server member. Leave blank or type \"me\" to test yourself."""
        mem: discord.Member = await converterplus.lookup_member(interaction, member)
        members = self.bot.db.read_many(Database.COLLECTION_MEMBERS)

        msg_count = 0
        total_msg_count = 0
        for m in members:
            total_msg_count += m.get("messageCount", 0)
            if m.get("_id") == str(mem.id):
                msg_count = m.get("messageCount", 0)

        msg_density = msg_count/total_msg_count
        role_str = await self.get_role_string(mem)
        embed = discord.Embed(color=mem.top_role.color, title=mem.name)
        embed.set_image(url=mem.display_avatar.with_size(128))
        embed.add_field(name="Mention", value=mem.mention)
        embed.add_field(name="Total Messages", value=(msg_count))
        embed.add_field(name="Message Density", value=(str(round(msg_density*100, 2))+"%"))
        embed.add_field(name="Roles", value=role_str, inline=False)
        embed.set_footer(text=f"Total Messages are counted since December 3rd, 2022. Serverwide count: {total_msg_count}")
        await interaction.response.send_message(content="", embed=embed)

async def setup(bot):
    await bot.add_cog(Stats(bot))