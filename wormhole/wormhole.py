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
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        if not message.guild:
            return
        
        source_id = str(message.channel.id)
        linked_channels = await self.config.get_raw("linked_channels")
        destination_id = linked_channels.get(source_id)
        
        if destination_id and message.channel.id == int(source_id):
            destination_channel = self.bot.get_channel(int(destination_id))
            if destination_channel:
                # Edit the webhook to reflect the user's profile picture and username
                webhooks = await destination_channel.webhooks()
                webhook = None
                for w in webhooks:
                    if w.user == self.bot.user:
                        webhook = w
                        break
                
                if webhook:
                    await webhook.edit(name=message.author.display_name, avatar=message.author.avatar_url)
    
    @commands.command()
    async def link(self, ctx, destination_channel: discord.TextChannel):
        """Link the current channel to a destination channel for sending messages."""
        source_channel_id = ctx.channel.id
        
        linked_channels = await self.config.get_raw("linked_channels")
        linked_channels[source_channel_id] = destination_channel.id
        await self.config.set_raw("linked_channels", value=linked_channels)
        
        # Create a webhook if it doesn't exist
        webhooks = await destination_channel.webhooks()
        webhook = None
        for w in webhooks:
            if w.user == self.bot.user:
                webhook = w
                break
            
        if not webhook:
            webhook = await destination_channel.create_webhook(name=self.bot.user.display_name)
        
        await ctx.send(f"This channel is now linked to the destination channel {destination_channel.mention}.")
    
def setup(bot):
    bot.add_cog(WormHole(bot))
