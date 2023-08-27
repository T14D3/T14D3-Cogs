import discord
from redbot.core import commands, Config

class ChannelLink(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890, force_registration=True)
        
    @commands.command()
    async def link(self, ctx, channel1_id: int, channel2_id: int):
        """Link two channels together."""
        channel1 = self.bot.get_channel(channel1_id)
        channel2 = self.bot.get_channel(channel2_id)
        
        if not channel1 or not channel2:
            await ctx.send("Invalid channel IDs provided.")
            return
        
        guild1 = channel1.guild
        guild2 = channel2.guild
        
        if guild1 == guild2:
            await ctx.send("Channels must be on different servers.")
            return
        
        config_key = f"linked_channels.{guild1.id}.{channel1.id}"
        await self.config.set_raw(config_key, value={"guild2_id": guild2.id, "channel2_id": channel2.id})
        
        await ctx.send(f"Channels {channel1.mention} and {channel2.mention} are now linked.")
    
    async def on_message(self, message):
        if message.author.bot:
            return
        
        channel_id = message.channel.id
        guild_id = message.guild.id
        
        linked_channels = await self.config.get_raw(f"linked_channels.{guild_id}.{channel_id}")
        
        if linked_channels:
            bot_guild = self.bot.get_guild(linked_channels["guild2_id"])
            bot_channel = bot_guild.get_channel(linked_channels["channel2_id"])
            
            if bot_channel:
                content = f"**{message.author.display_name}:** {message.content}"
                await bot_channel.send(content)
    
def setup(bot):
    bot.add_cog(ChannelLink(bot))
