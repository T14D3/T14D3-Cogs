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
    async def list_links(self, ctx):
        """List all linked channel pairs."""
        
        linked_channels = await self.config.get_raw("linked_channels", default={})
        linked_pairs = [
            (source_id, dest_id)
            for source_id, dest_id in linked_channels.items()
        ]
        
        if not linked_pairs:
            await ctx.send("There are no linked channel pairs.")
            return
        
        linked_pairs_info = "\n".join([f"Source Channel ID: {source_id} | Destination Channel ID: {dest_id}" for source_id, dest_id in linked_pairs])
        await ctx.send("Linked channel pairs:\n" + linked_pairs_info)
    
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
            webhook = await destination_channel.create_webhook(name=message.author.display_name)
        
        await webhook.send(message.content, username=message.author.display_name, avatar_url=str(message.author.avatar.url) if message.author.avatar else None)
    
    async def find_bot_webhook(self, channel):
        webhooks = await channel.webhooks()
        for webhook in webhooks:
            if webhook.token is None and webhook.user == self.bot.user:
                return webhook
        return None

def setup(bot):
    bot.add_cog(WormHole(bot))
