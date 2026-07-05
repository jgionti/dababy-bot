import discord
from discord.ext import commands

#####################
#   converterplus   #
#####################
# Introduces a more lenient Converter
# Includes case insensitivity and more!

# More general algorithm to look for member
# Return: Member
# Raises: MemberNotFound
async def lookup_member(interaction: discord.Interaction, target: str) -> discord.Member:
    # Check if user asking about themselves
    if (target.lower() == "me"):
        return interaction.user
    
    found = False
    # 1. Try the converter
    converter = commands.MemberConverter()
    try:
        member = await converter.convert(await commands.Context.from_interaction(interaction), target)
        found = True
    except:
        # 2. Compare lowercase string with all member names
        for mem in interaction.guild.members:
            if (target.lower() == mem.name.lower()):
                member = mem
                found = True
                break
        # 3. Compare lowercase string with all member top roles (for real names)
        if not found:
            for mem in interaction.guild.members:
                if (target.lower() == mem.top_role.name.lower()):
                    member = mem
                    found = True
                    break
        # 4. Compare lowercase string with all member nicknames
        if not found:
            for mem in interaction.guild.members:
                if mem.nick:
                    if (target.lower() == mem.nick.lower()):
                        member = mem
                        found = True
                        break
        # 5. Compare lowercase string with first word of all member names
        if not found:
            for mem in interaction.guild.members:
                mem_split = mem.name.split(" ")
                for word in mem_split:
                    if (target.lower() == word.lower()):
                        member = mem
                        found = True
                        break
                if found:
                    break
    if found:
        return member
    raise commands.MemberNotFound(target)

# More general algorithm to look for role
# Return: Role
# Raises: RoleNotFound
async def lookup_role(interaction: discord.Interaction, target: str) -> discord.Role:
    found = False
    # 1. Try the converter
    converter = commands.RoleConverter()
    try:
        role = await converter.convert(await commands.Context.from_interaction(interaction), target)
        found = True
    except:
        # 2. Compare lowercase string with all role names
        for rle in interaction.guild.roles:
            if (target.lower() == rle.name.lower()):
                role = rle
                found = True
        # 3. Compare lowercasse string with first word of all role names
        for rle in interaction.guild.roles:
            rle_split = rle.name.split(" ")
            if (target.lower() == rle_split[0].lower()):
                role = rle
                found = True
    if found:
        return role
    raise commands.RoleNotFound(target)

# Textchannel converter
# Return: TextChannel
# Raises: ChannelNotFound
async def lookup_textchannel(interaction: discord.Interaction, target: str) -> discord.TextChannel:
    # 1. Try the converter
    converter = commands.TextChannelConverter()
    textchannel = await converter.convert(await commands.Context.from_interaction(interaction), target)
    return textchannel

# Textchannel converter
# Return: Thread
# Raises: ThreadNotFound
async def lookup_thread(interaction: discord.Interaction, target: str) -> discord.Thread:
    # 1. Try the converter
    converter = commands.ThreadConverter()
    thread = await converter.convert(await commands.Context.from_interaction(interaction), target)
    return thread
