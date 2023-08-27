import discord
from redbot.core import commands, Config

class WormHole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier="wormhole", force_registration=True)
        self.config.register_global(linked_channels={})
        
    @commands.command()
    async def link(self, ctx, destination_channel_id: int):
        """Link the current channel to a destination channel for sending messages."""
        source_channel_id = ctx.channel.id
        
        linked_channels = await self.config.linked_channels()
        linked_channels[source_channel_id] = destination_channel_id
        await self.config.linked_channels.set(linked_channels)
        
        await ctx.send(f"This channel is now linked to the destination channel with ID {destination_channel_id}.")
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.guild is None:  # Ignore messages from bots and DMs
            return
        if not message.channel.permissions_for(message.guild.me).send_messages:
            return
        
        source_channel_id = message.channel.id
        
        linked_channels = await self.config.linked_channels()
        destination_channel_id = linked_channels.get(source_channel_id)
        
        if destination_channel_id is not None:
            destination_channel = self.bot.get_channel(destination_channel_id)
            
            if destination_channel:
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
