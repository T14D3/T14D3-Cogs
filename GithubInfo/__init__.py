from .githubinfo import githubstarupdater

async def setup(bot):
    cog = githubstarupdater(bot)
    await bot.add_cog(cog)
