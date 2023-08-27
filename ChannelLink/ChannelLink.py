import discord
from redbot.core import commands, Config

class ChannelLink(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier="wormhole", force_registration=True)
        
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
        
        link_data = {
            "guild1_id": guild1.id,
            "channel1_id": channel1.id,
            "guild2_id": guild2.id,
            "channel2_id": channel2.id
        }
        
        config_key = f"linked_channels.{guild1.id}.{channel1.id}"
        await self.config.set_raw(config_key, value=link_data)
        
        await ctx.send(f"Channels {channel1.mention} and {channel2.mention} are now linked.")
    
    async def on_message(self, message):
        if message.author.bot:
            return
        
        channel_id = message.channel.id
        guild_id = message.guild.id
        
        linked_channels = await self.config.get_raw(f"linked_channels.{guild_id}.{channel_id}")
        
        if linked_channels:
            if linked_channels["guild1_id"] == guild_id and linked_channels["channel1_id"] == channel_id:
                target_guild_id = linked_channels["guild2_id"]
                target_channel_id = linked_channels["channel2_id"]
            elif linked_channels["guild2_id"] == guild_id and linked_channels["channel2_id"] == channel_id:
                target_guild_id = linked_channels["guild1_id"]
                target_channel_id = linked_channels["channel1_id"]
            else:
                return
            
            bot_guild = self.bot.get_guild(target_guild_id)
            bot_channel = bot_guild.get_channel(target_channel_id)
            
            if bot_channel:
                content = f"**{message.author.display_name}:** {message.content}"
                await bot_channel.send(content)
    
def setup(bot):
    bot.add_cog(ChannelLink(bot))
