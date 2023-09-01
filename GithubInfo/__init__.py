from .githubinfo import GithubStarUpdater

async def setup(bot):
    cog = GithubStarUpdater(bot)
    await bot.add_cog(cog)
