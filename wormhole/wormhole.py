import discord
from redbot.core import commands

class WormHole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def sendmessage(self, ctx, channel_id: int, *, message: str):
        """Send a message to a specific channel using a webhook."""
        channel = self.bot.get_channel(channel_id)
        
        if not channel:
            await ctx.send("Invalid channel ID provided.")
            return
        
        # Create a webhook with the user's profile picture and name
        webhook = await channel.create_webhook(name=ctx.author.display_name, avatar=ctx.author.avatar_url)
        
        # Send the message using the webhook
        await webhook.send(message, username=ctx.author.display_name, avatar_url=ctx.author.avatar_url)
        
        await ctx.send(f"Message sent to {channel.mention} using your profile information.")
    
def setup(bot):
    bot.add_cog(WormHole(bot))
