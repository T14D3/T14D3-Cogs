import discord
from redbot.core import commands, Config, checks
import aiohttp
import asyncio

class GithubInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890, force_registration=True)
        default_global = {
            "channel_repo_mappings": {},  # Mapping of voice channels to GitHub repo URLs
        }
        self.config.register_global(**default_global)
        
        # Start the update loop
        self.bot.loop.create_task(self.update_star_channels())

    async def fetch_stars(self, repo_url, api_key):
        headers = {
            "Authorization": f"Bearer {api_key}",
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{repo_url}/stargazers", headers=headers) as response:
                data = await response.json()
                return len(data)

    async def update_star_channels(self):
        await self.bot.wait_until_ready()
        while True:
            github_keys = await self.bot.get_shared_api_tokens("github")
            api_key = github_keys.get("api_key")
            if api_key:
                channel_mappings = await self.config.channel_repo_mappings()
                for channel_id, repo_url in channel_mappings.items():
                    try:
                        channel = self.bot.get_channel(int(channel_id))
                        if channel:
                            stars = await self.fetch_stars(repo_url, api_key)
                            await channel.edit(name=f"{stars} Stars")
                    except Exception as e:
                        print(f"Error updating channel: {e}")
            await asyncio.sleep(300)  # 5 minutes

    @commands.group()
    async def github(self, ctx):
        """GitHub related commands."""
        pass

    @github.command()
    async def setrepo(self, ctx, channel: discord.VoiceChannel, repo_url: str):
        """Set a GitHub repo for a voice channel."""
        await self.config.channel_repo_mappings.set_raw(
            str(channel.id), value=repo_url
        )
        await ctx.send(f"GitHub repo set for {channel.mention}.")
