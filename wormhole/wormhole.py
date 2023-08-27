import discord
from redbot.core import commands, Config

class WormHole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier="wormhole", force_registration=True)
        self.config.register_global(linked_channels_list=[])  # Initialize the configuration
        
        # Start setup listeners when the bot is ready
        self.bot.loop.create_task(self.setup_listeners())
        
    async def setup_listeners(self):
        await self.bot.wait_until_ready()
        # Add the on_source_message listener to the on_message event
        self.bot.add_listener(self.on_source_message, "on_message")
    
    async def send_status_message(self, message, channel):
        linked_channels = await self.config.linked_channels_list()
        for webhook_id, channel_id in linked_channels:
            relay_channel = self.bot.get_channel(channel_id)
            if relay_channel and relay_channel != channel:
                await relay_channel.send(f"**Status:** {message}")
    
    @commands.command()
    async def link(self, ctx):
        """Link the current channel to the network and create a webhook."""
        linked_channels = await self.config.linked_channels_list()
        if ctx.channel.id not in [pair[1] for pair in linked_channels]:
            # Create a webhook in the current channel
            webhook = await ctx.channel.create_webhook(name="Wormhole Webhook")
            
            # Add the webhook ID and channel ID pair to the list
            linked_channels.append((webhook.id, ctx.channel.id))
            await self.config.linked_channels_list.set(linked_channels)
            
            # Inform the user
            await ctx.send("This channel is now linked to the network.")
            
            # Send a status message to connected channels
            await self.send_status_message(f"Channel {ctx.channel.mention} has been added to the network.", ctx.channel)
        else:
            await ctx.send("This channel is already linked.")
    
    @commands.command()
    async def unlink(self, ctx):
        """Unlink the current channel from the network and delete the associated webhook."""
        linked_channels = await self.config.linked_channels_list()
        webhook_id_to_remove = None
        for webhook_id, channel_id in linked_channels:
            if channel_id == ctx.channel.id:
                webhook_id_to_remove = webhook_id
                break
        
        if webhook_id_to_remove:
            # Remove the webhook ID and channel ID pair from the list
            linked_channels = [(webhook_id, channel_id) for webhook_id, channel_id in linked_channels if webhook_id != webhook_id_to_remove]
            await self.config.linked_channels_list.set(linked_channels)
            
            # Delete the webhook
            webhook = discord.Webhook.partial(webhook_id_to_remove, token=None, session=self.bot.http._session)
            await webhook.delete()
            
            # Inform the user
            await ctx.send("This channel is no longer linked to the network.")
            
            # Send a status message to connected channels
            await self.send_status_message(f"Channel {ctx.channel.mention} has been removed from the network.", ctx.channel)
        else:
            await ctx.send("This channel is not linked.")
    
    @commands.Cog.listener()
    async def on_message_without_command(self, message: discord.Message):
        if not message.guild:  # Don't allow in DMs
            return
        if message.author.bot or not message.channel.permissions_for(message.guild.me).send_messages:
            return
        if isinstance(message.channel, discord.TextChannel) and message.content.startswith(commands.when_mentioned(self.bot, message)[0]):
            return  # Ignore bot commands
        
        linked_channels = await self.config.linked_channels_list()
        if message.channel.id in [pair[1] for pair in linked_channels]:
            for webhook_id, channel_id in linked_channels:
                if channel_id != message.channel.id:
                    # Retrieve the webhook and send the message
                    webhook = discord.Webhook.partial(webhook_id, token=None, session=self.bot.http._session)
                    await webhook.send(f"**{message.author.display_name}:** {message.content}")
                    break  # Send only to the first linked channel
    
def setup(bot):
    bot.add_cog(WormHole(bot))
