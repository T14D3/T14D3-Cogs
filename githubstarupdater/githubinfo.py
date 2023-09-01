import discord
from redbot.core import commands
from github import Github, GithubException

class githubstarupdater(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def fetch_stars(self, repo_url, api_key):
        try:
            # Initialize PyGithub with the access token
            auth = Github(api_key)
            
            # Extract owner and repo name from the URL
            parts = repo_url.strip("/").split("/")
            if len(parts) >= 2:
                owner = parts[-2]
                repo_name = parts[-1]

                repo = auth.get_repo(f"{owner}/{repo_name}")
                stars = repo.stargazers_count
                return stars
        except GithubException as e:
            print(f"GitHub API error: {e}")
        except Exception as e:
            print(f"Failed to fetch stars: {e}")

        return None

    @commands.command()
    async def updatestars(self, ctx, channel: discord.VoiceChannel, repo_url: str, message_format: str):
        """Update the channel's name with the star count of a GitHub repository."""
        github_keys = await self.bot.get_shared_api_tokens("github")
        api_key = github_keys.get("api_key")
        if api_key:
            stars = await self.fetch_stars(repo_url, api_key)
            if stars is not None:
                updated_name = message_format.replace("{count}", str(stars))
                await channel.edit(name=updated_name)
                await ctx.send(f"Updated {channel.mention} with {stars} Stars.")
            else:
                await ctx.send(f"Failed to fetch stars for {repo_url}.")
        else:
            await ctx.send("GitHub API key is not set. Please set it using Red's API store.")
