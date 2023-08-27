from .ChannelLink import ChannelLink

async def setup(bot):
    await bot.add_cog(ChannelLink(bot))
