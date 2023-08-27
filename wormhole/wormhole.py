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
    async def show_links(self, ctx):
        """Show all linked channel pairs for this channel."""
        source_channel_id = ctx.channel.id
        
        linked_channels = await self.config.get_raw("linked_channels", default={})
        linked_pairs = [
            (source_id, dest_id)
            for source_id, dest_id in linked_channels.items()
            if dest_id == source_channel_id
        ]
        
        if not linked_pairs:
            await ctx.send("This channel is not linked to any destination channels.")
            return
        
        response = "Linked channel pairs:\n"
        for source_id, _ in linked_pairs:
            response += f"Source Channel ID: {source_id}\n"
        
        await ctx.send(response)
    
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
