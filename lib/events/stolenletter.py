import re

import discord
from lib.events.event import Event


class StolenLetterEvent(Event):
    """Event class for the Stolen Letter event.

    Messages with the stolen letter are replaced with webhooks that
    remove all instances of the letter.
    """
    def __init__(self, bot):
        super().__init__(bot, aliases=["stolenletter"])
        self.stolen_char = 'n'

    async def start(self, ctx, args):
        # Initialize event
        if len(args) > 0:
            stolen_char = args[0]
            if len(stolen_char) != 1:
                await ctx.respond("\N{CROSS MARK} Only 1 character allowed!", ephemeral = True)
                return
            self.stolen_char = stolen_char.lower()

        # Filter message and send
        msg = "Okay, very funny guys. Who snatched the letter \'" + self.stolen_char + "\'? " + \
            "This is actually a quite bad jump from before! **(All messages with the exiled letter will be zapped)**"
        msg = msg.replace(self.stolen_char, '')
        msg = msg.replace(self.stolen_char.upper(), '')
        await ctx.respond(content=msg, file=discord.File("resources/StolenLetter.PNG"))
        await super().start(ctx)

    async def end(self, ctx, args):
        await super().end(ctx, args)
        await ctx.respond("Let's go! The letter \'" + self.stolen_char + "\' has been found again!")

    async def on_message(self, message: discord.Message):
        if self.is_active:
            if self.stolen_char in message.content.lower() and message.webhook_id == None:
                webhook: discord.Webhook = await message.channel.create_webhook(name=message.author.display_name)
                msg = re.sub(self.stolen_char, "", message.content, flags = re.I)
                await message.delete()
                await webhook.send(msg, username=message.author.display_name, avatar_url=message.author.avatar.url)
                await webhook.delete()
