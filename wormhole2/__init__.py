from .wormhole2 import WormHole2

async def setup(bot):
    await bot.add_cog(WormHole2(bot))
