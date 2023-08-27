import discord
from redbot.core import commands, Config

class WormHole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier="wormhole", force_registration=True)
        
    @commands.command()
    async def link(self, ctx, destination_channel_id: int):
        """Link the current channel to a destination channel for sending messages."""
        source_channel_id = ctx.channel.id
        
        await self.config.set_raw(f"linked_channels.{source_channel_id}", value=destination_channel_id)
        
        await ctx.send(f"This channel is now linked to the destination channel with ID {destination_channel_id}.")
    
    @commands.command()
    async def sendmessage(self, ctx, *, message: str):
        """Send a message to the linked destination channel using a webhook."""
        source_channel_id = ctx.channel.id
        
        destination_channel_id = await self.config.get_raw(f"linked_channels.{source_channel_id}")
        if not destination_channel_id:
            await ctx.send("This channel is not linked to a destination channel.")
            return
        
        destination_channel = self.bot.get_channel(destination_channel_id)
        
        if not destination_channel:
            await ctx.send("The linked destination channel does not exist.")
            return
        
        webhook = await self.find_bot_webhook(destination_channel)
        
        if webhook:
            await webhook.send(message, username=ctx.author.display_name, avatar_url=str(ctx.author.avatar.url) if ctx.author.avatar else None)
            await ctx.send(f"Message sent to the linked destination channel using your profile information.")
        else:
            await ctx.send("Webhook not found in the destination channel. Please make sure the bot has the necessary permissions.")
    
    async def find_bot_webhook(self, channel):
        webhooks = await channel.webhooks()
        for webhook in webhooks:
            if webhook.token is None and webhook.user == self.bot.user:
                return webhook
        return None

def setup(bot):
    bot.add_cog(WormHole(bot))
