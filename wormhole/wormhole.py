import discord
from redbot.core import commands

class WormHole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def sendmessage(self, ctx, channel_id: int, *, message: str):
        """Send a message to a specific channel."""
        channel = self.bot.get_channel(channel_id)
        
        if not channel:
            await ctx.send("Invalid channel ID provided.")
            return
        
        await channel.send(message)
        await ctx.send(f"Message sent to {channel.mention}.")
    
def setup(bot):
    bot.add_cog(WormHole(bot))
