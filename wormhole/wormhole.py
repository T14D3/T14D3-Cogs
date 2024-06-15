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
    
    async def send_status_message(self, message, channel):
        linked_channels = await self.config.linked_channels_list()
        guild = channel.guild
        for channel_id in linked_channels:
            relay_channel = self.bot.get_channel(channel_id)
            if relay_channel and relay_channel != channel:
                await relay_channel.send(f"***The wormhole is shifting...** {guild.name}: {message}*")
    
    @commands.group()
    async def wormhole(self, ctx):
        """Manage wormhole connections."""
        pass
    
    @wormhole.command(name="open")
    async def wormhole_open(self, ctx):
        """Link the current channel to the network."""
        linked_channels = await self.config.linked_channels_list()
        if ctx.channel.id not in linked_channels:
            linked_channels.append(ctx.channel.id)
            await self.config.linked_channels_list.set(linked_channels)
            await ctx.send("This channel has joined the ever-changing maelstrom that is the wormhole.")
            await self.send_status_message(f"A faint signal was picked up from {ctx.channel.mention}, connection has been established.", ctx.channel)
        else:
            await ctx.send("This channel is already part of the wormhole.")
    
    @wormhole.command(name="close")
    async def wormhole_close(self, ctx):
        """Unlink the current channel from the network."""
        linked_channels = await self.config.linked_channels_list()
        if ctx.channel.id in linked_channels:
            linked_channels.remove(ctx.channel.id)
            await self.config.linked_channels_list.set(linked_channels)
            await ctx.send("This channel has been severed from the wormhole.")
            await self.send_status_message(f"The signal from {ctx.channel.mention} has become too faint to be picked up, the connection was lost.", ctx.channel)
        else:
            await ctx.send("This channel is not part of the wormhole.")
    
    @wormhole.command(name="setrank")
    async def wormhole_set_rank(self, ctx, member: discord.Member, role_name: str):
        """Set the displayed rank for a member in the guild."""
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role:
            await self.config.guild(ctx.guild).set_raw(f"member_{member.id}", value=role.id)
            await ctx.send(f"The displayed rank for {member.display_name} has been set to {role_name}.")
        else:
            await ctx.send(f"Role '{role_name}' not found in the guild.")
    
    @commands.Cog.listener()
    async def on_message_without_command(self, message: discord.Message):
        if not message.guild:  # don't allow in DMs
            return
        if message.author.bot or not message.channel.permissions_for(message.guild.me).send_messages:
            return
        if isinstance(message.channel, discord.TextChannel) and message.content.startswith(commands.when_mentioned(self.bot, message)[0]):
            return  # Ignore bot commands
        
        linked_channels = await self.config.linked_channels_list()
        guild = message.guild
        author = message.author
        if message.channel.id in linked_channels:
            for channel_id in linked_channels:
                if channel_id != message.channel.id:
                    channel = self.bot.get_channel(channel_id)
                    if channel:
                        display_name = author.display_name if author.display_name else author.name
                        await channel.send(f"**{guild.name} - {display_name}:** {message.content}")
    
def setup(bot):
    bot.add_cog(WormHole(bot))
