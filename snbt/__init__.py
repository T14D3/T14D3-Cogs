from .snbt import SNBT

async def setup(bot):
    await bot.add_cog(SNBT(bot))
