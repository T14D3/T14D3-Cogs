import discord
from redbot.core import commands, Config
import aiohttp

class WormHole2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier="wormhole2", force_registration=True)
        self.config.register_global(linked_channels_list=[])  # Initialize the configuration
        self.webhook_cache = {}

        self.bot.loop.create_task(self.setup_listeners())
        
    async def setup_listeners(self):
        await self.bot.wait_until_ready()
        self.bot.add_listener(self.on_message_without_command, "on_message")
    
    async def send_status_message(self, message, channel):
        linked_channels = await self.config.linked_channels_list()
        guild = channel.guild
        for channel_id in linked_channels:
            relay_channel = self.bot.get_channel(channel_id)
            if relay_channel and relay_channel != channel:
                await relay_channel.send(f"***The wormhole is shifting...** {guild.name}: {message}*")
    
    @commands.group()
    async def wormhole2(self, ctx):
        """Manage wormhole connections."""
        pass
    
    @wormhole2.command(name="open")
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
    
    @wormhole2.command(name="close")
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
    
    async def get_webhook(self, channel):
        if channel.id in self.webhook_cache:
            return self.webhook_cache[channel.id]
        webhooks = await channel.webhooks()
        for webhook in webhooks:
            if webhook.user == self.bot.user:
                self.webhook_cache[channel.id] = webhook
                return webhook
        webhook = await channel.create_webhook(name="Wormhole Relay")
        self.webhook_cache[channel.id] = webhook
        return webhook
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild:  # don't allow in DMs
            return
        if message.author.bot or not message.channel.permissions_for(message.guild.me).send_messages:
            return
        if isinstance(message.channel, discord.TextChannel) and message.content.startswith(commands.when_mentioned(self.bot, message)[0]):
            return  # Ignore bot commands
        
        linked_channels = await self.config.linked_channels_list()
        if message.channel.id in linked_channels:
            for channel_id in linked_channels:
                if channel_id != message.channel.id:
                    relay_channel = self.bot.get_channel(channel_id)
                    if relay_channel:
                        webhook = await self.get_webhook(relay_channel)
                        await webhook.send(
                            content=message.content,
                            username=message.author.display_name,
                            avatar_url=message.author.avatar.url
                        )

def setup(bot):
    bot.add_cog(WormHole2(bot))
