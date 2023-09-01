from .wormhole import WormHole

async def setup(bot):
    await bot.add_cog(WormHole(bot))
