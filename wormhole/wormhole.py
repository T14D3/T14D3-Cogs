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
        linked_channels = await self.config.linked_channels()
        for source_id, destination_id in linked_channels.items():
            source_channel = self.bot.get_channel(int(source_id))
            if source_channel:
                self.bot.add_listener(self.on_source_message, "on_message", source=source_channel)  # Add listener for specific channel
    
    @commands.command()
    async def link(self, ctx, destination_channel_id: int):
        """Link the current channel to a destination channel for sending messages."""
        source_channel_id = ctx.channel.id
        
        linked_channels = await self.config.linked_channels()
        linked_channels[source_channel_id] = destination_channel_id
        await self.config.linked_channels.set(linked_channels)
        
        await ctx.send(f"This channel is now linked to the destination channel with ID {destination_channel_id}.")
    
    @commands.command()
    async def unlink(self, ctx, source_channel: discord.TextChannel):
        """Unlink the specified source channel."""
        source_channel_id = source_channel.id
        
        linked_channels = await self.config.linked_channels()
        if source_channel_id in linked_channels:
            del linked_channels[source_channel_id]
            await self.config.linked_channels.set(linked_channels)
            await ctx.send(f"This channel is no longer linked to any destination channel.")
        else:
            await ctx.send(f"This channel is not linked to any destination channel.")
    
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
            linked_channels = await self.config.linked_channels()
            destination_id = linked_channels.get(source_id)
            
            if destination_id and message.channel.id == int(source_id):
                destination_channel = self.bot.get_channel(int(destination_id))
                if destination_channel:
                    await destination_channel.send(f"**{message.author.display_name}:** {message.content}")
    
def setup(bot):
    bot.add_cog(WormHole(bot))
