import discord
from redbot.core import commands
from github import Github

class githubstarupdater(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def fetch_stars(self, repo_url, api_key):
        # Initialize PyGithub with the access token
        g = Github(api_key)
        
        repo_parts = repo_url.strip("/").split("/")
        if len(repo_parts) == 2:
            owner, repo_name = repo_parts
            try:
                repo = g.get_repo(f"{owner}/{repo_name}")
                stars = repo.stargazers_count
                return stars
            except Exception as e:
                print(f"Failed to fetch stars: {e}")
        return None

    @commands.command()
    async def updatestars(self, ctx, channel: discord.VoiceChannel, repo_url: str):
        """Update the channel's name with the star count of a GitHub repository."""
        github_keys = await self.bot.get_shared_api_tokens("github")
        api_key = github_keys.get("api_key")
        if api_key:
            stars = await self.fetch_stars(repo_url, api_key)
            if stars is not None:
                await channel.edit(name=f"{stars} Stars")
                await ctx.send(f"Updated {channel.mention} with {stars} Stars.")
            else:
                await ctx.send(f"Failed to fetch stars for {repo_url}.")
        else:
            await ctx.send("GitHub API key is not set. Please set it using Red's API store.")
