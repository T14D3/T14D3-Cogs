import discord
from redbot.core import commands, Config

class WormHole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier="wormhole", force_registration=True)
        self.config.register_global(linked_channels={})  # Initialize the configuration
        
        self.bot.loop.create_task(self.setup_listeners())
        
    async def setup_listeners(self):
        await self.bot.wait_until_ready()
        linked_channels = await self.config.get_raw("linked_channels")
        for source_id, destination_id in linked_channels.items():
            source_channel = self.bot.get_channel(int(source_id))
            if source_channel:
                self.bot.add_listener(self.on_source_message, "on_message", check=lambda message: message.channel == source_channel)
    
    @commands.command()
    async def link(self, ctx, destination_channel_id: int):
        """Link the current channel to a destination channel for sending messages."""
        source_channel_id = ctx.channel.id
        
        linked_channels = await self.config.get_raw("linked_channels")
        linked_channels[source_channel_id] = destination_channel_id
        await self.config.set_raw("linked_channels", value=linked_channels)
        
        await ctx.send(f"This channel is now linked to the destination channel with ID {destination_channel_id}.")
    
    @commands.Cog.listener()
    async def on_message_without_command(self, message: discord.Message):
        if not message.guild:  # don't allow in DMs
            return
        if not message.channel.permissions_for(message.guild.me).send_messages:
            return
        await self.on_source_message(message)
    
    async def on_source_message(self, message):
        if not message.author.bot:
            source_id = str(message.channel.id)
            linked_channels = await self.config.get_raw("linked_channels")
            destination_id = linked_channels.get(source_id)
            
            if destination_id:
                destination_channel = self.bot.get_channel(int(destination_id))
                if destination_channel:
                    webhook = await self.find_bot_webhook(destination_channel)
                    if not webhook:
                        # Create a new webhook with the user's profile picture and name
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
