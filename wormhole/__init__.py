from .wormhole import wormhole

async def setup(bot):
    await bot.add_cog(wormhole(bot))
