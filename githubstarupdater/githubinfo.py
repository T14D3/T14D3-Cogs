import discord
from redbot.core import commands
import aiohttp

class githubstarupdater(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def fetch_stars(self, repo_url, api_key):
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/vnd.github.v3+json",  # Specify JSON response
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{repo_url}/stargazers", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return len(data)
                else:
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
