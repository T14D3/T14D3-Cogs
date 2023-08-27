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
    
    @commands.Cog.listener()
    async def on_message_without_command(self, message: discord.Message):
        if not message.guild:  # don't allow in DMs
            return
        if not message.channel.permissions_for(message.guild.me).send_messages:
            return
        await self.some_command_function(message)
    
    async def some_command_function(self, message: discord.Message):
        source_channel_id = message.channel.id
        
        destination_channel_id = await self.config.get_raw(f"linked_channels.{source_channel_id}")
        if not destination_channel_id:
            return
        
        destination_channel = self.bot.get_channel(destination_channel_id)
        
        if not destination_channel:
            return
        
        content = f'I heard you say "{message.content}"'
        await destination_channel.send(content)
    
    async def find_bot_webhook(self, channel):
        webhooks = await channel.webhooks()
        for webhook in webhooks:
            if webhook.token is None and webhook.user == self.bot.user:
                return webhook
        return None

def setup(bot):
    bot.add_cog(WormHole(bot))
