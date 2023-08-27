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
        
        linked_channels = await self.config.linked_channels()
        
        if source_channel_id in linked_channels:
            await ctx.send("This channel is already linked to a destination channel.")
            return
        
        linked_channels[source_channel_id] = destination_channel_id
        await self.config.linked_channels.set(linked_channels)
        
        await ctx.send(f"This channel is now linked to the destination channel with ID {destination_channel_id}.")


    
    
    @commands.Cog.listener()
    async def on_message_without_command(self, message: discord.Message):
        if message.author.bot or message.guild is None:  # Ignore messages from bots and DMs
            return
        if not message.channel.permissions_for(message.guild.me).send_messages:
            return
        await self.send_message_through_webhook(message)
    
    async def send_message_through_webhook(self, message: discord.Message):
        source_channel_id = message.channel.id
        
        destination_channel_id = await self.config.get_raw(f"linked_channels.{source_channel_id}")
        if not destination_channel_id:
            return
        
        destination_channel = self.bot.get_channel(destination_channel_id)
        
        if not destination_channel:
            return
        
        webhook = await self.find_bot_webhook(destination_channel)
        
        if not webhook:
            return
        
        await webhook.edit(name=message.author.display_name, avatar=None if not message.author.avatar else await message.author.avatar.read(), reason="Webhook update")
        await webhook.send(message.content)
    
    async def find_bot_webhook(self, channel):
        webhooks = await channel.webhooks()
        for webhook in webhooks:
            if webhook.token is None and webhook.user == self.bot.user:
                return webhook
        return None

def setup(bot):
    bot.add_cog(WormHole(bot))
