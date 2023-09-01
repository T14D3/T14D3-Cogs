from .githubinfo import GithubInfo

async def setup(bot):
    cog = GithubInfo(bot)
    await bot.add_cog(cog)
    # Register the GitHub API token key
    await bot.register_shared_api_token("github", "api_key")
