import discord
from redbot.core import commands
from github import Github

class GithubInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def githubstars(self, ctx, repo_owner, repo_name):
        github_keys = await self.bot.get_shared_api_tokens("github")
        github_token = github_keys.get("api_key")

        if github_token is None:
            return await ctx.send("The GitHub API token has not been set. Please ask a bot administrator to set it using `[p]set api github api_key,TOKEN`.")

        # Create a GitHub instance
        github = Github(github_token)

        try:
            # Get the repository
            repo = github.get_repo(f"{repo_owner}/{repo_name}")

            # Get the number of stars
            stars = repo.stargazers_count

            # Send the stars count to the Discord channel
            await ctx.send(f"{stars}")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

def setup(bot):
    bot.add_cog(GithubInfo(bot))
