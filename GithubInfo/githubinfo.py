import discord
from redbot.core import commands, Config
from github import Github
import asyncio

class GithubInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)  # Change the identifier to a unique integer
        self.config.register_global(github_token=None, text_template="GitHub Stars: {}")
        self.task = None

    async def update_voice_channel(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            github_keys = await self.bot.get_shared_api_tokens("github")
            github_token = github_keys.get("api_key")

            if github_token is not None:
                # Create a GitHub instance
                github = Github(github_token)

                try:
                    # Get the repository (replace owner and repo_name with your values)
                    repo = github.get_repo("owner/repo_name")

                    # Get the number of stars
                    stars = repo.stargazers_count

                    # Get the configured text template
                    text_template = await self.config.text_template()

                    # Update the voice channel names in all guilds
                    for guild in self.bot.guilds:
                        for channel in guild.voice_channels:
                            if channel.id == int(channel_id):
                                new_name = text_template.format(stars)
                                await channel.edit(name=new_name)
                except Exception as e:
                    print(f"An error occurred: {str(e)}")

            await asyncio.sleep(300)  # Sleep for 5 minutes

    @commands.command()
    async def settexttemplate(self, ctx, *, template: str):
        """Set the text template for the voice channel name."""
        await self.config.text_template.set(template)
        await ctx.send("Text template set successfully.")

    @commands.command()
    async def startgithubstars(self, ctx, channel_id: int):
        """Start updating a voice channel with GitHub stars count."""
        if self.task and not self.task.done():
            return await ctx.send("The GitHub stars update task is already running.")

        self.task = self.bot.loop.create_task(self.update_voice_channel())
        await ctx.send(f"GitHub stars updates started for Voice Channel ID {channel_id}.")

    @commands.command()
    async def stopgithubstars(self, ctx):
        """Stop updating the voice channel with GitHub stars count."""
        if self.task and not self.task.done():
            self.task.cancel()
            await ctx.send("GitHub stars updates stopped.")
        else:
            await ctx.send("No GitHub stars update task is currently running.")

def setup(bot):
    bot.add_cog(GithubInfo(bot))
