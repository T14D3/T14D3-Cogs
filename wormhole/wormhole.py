import discord
from redbot.core import commands, Config

class WormHole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier="wormhole", force_registration=True)
        self.config.register_global(linked_channels_list=[])  # Initialize the configuration
        
        self.bot.loop.create_task(self.setup_listeners())
        
    async def setup_listeners(self):
        await self.bot.wait_until_ready()
        self.bot.add_listener(self.on_source_message, "on_message")
    
    @commands.command()
    async def link(self, ctx):
        """Link the current channel to the network."""
        linked_channels = await self.config.linked_channels_list()
        if ctx.channel.id not in linked_channels:
            linked_channels.append(ctx.channel.id)
            await self.config.linked_channels_list.set(linked_channels)
            await ctx.send("This channel is now linked to the network.")
        else:
            await ctx.send("This channel is already linked.")
    
    @commands.command()
    async def unlink(self, ctx):
        """Unlink the current channel from the network."""
        linked_channels = await self.config.linked_channels_list()
        if ctx.channel.id in linked_channels:
            linked_channels.remove(ctx.channel.id)
            await self.config.linked_channels_list.set(linked_channels)
            await ctx.send("This channel is no longer linked to the network.")
        else:
            await ctx.send("This channel is not linked.")
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild:  # don't allow in DMs
            return
        if not message.channel.permissions_for(message.guild.me).send_messages:
            return
        
        linked_channels = await self.config.linked_channels_list()
        if message.channel.id in linked_channels:
            for channel_id in linked_channels:
                if channel_id != message.channel.id:
                    channel = self.bot.get_channel(channel_id)
                    if channel:
                        await channel.send(f"**{message.author.display_name}:** {message.content}")
    
def setup(bot):
    bot.add_cog(WormHole(bot))
