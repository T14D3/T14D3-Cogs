from .githubinfo import GithubInfo

async def setup(bot):
    await bot.add_cog(GithubInfo(bot))