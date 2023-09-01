from .githubinfo import GithubInfo

async def setup(bot):
    cog = GithubInfo(bot)
    await bot.add_cog(cog)
