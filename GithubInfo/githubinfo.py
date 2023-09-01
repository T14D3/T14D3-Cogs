import discord
from redbot.core import commands
import aiohttp

class githubstarupdater(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def fetch_stars(self, repo_url, api_key):
        headers = {
            "Authorization": f"Bearer {api_key}",
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{repo_url}/stargazers", headers=headers) as response:
                data = await response.json()
                return len(data)

    @commands.command()
    async def updatestars(self, ctx, channel: discord.TextChannel, repo_url: str):
        """Update the channel's name with the star count of a GitHub repository."""
        github_keys = await self.bot.get_shared_api_tokens("github")
        api_key = github_keys.get("api_key")
        if api_key:
            stars = await self.fetch_stars(repo_url, api_key)
            await channel.edit(name=f"{stars} Stars")
            await ctx.send(f"Updated {channel.mention} with {stars} Stars.")
        else:
            await ctx.send("GitHub API key is not set. Please set it using Red's API store.")
