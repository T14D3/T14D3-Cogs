import discord
from redbot.core import commands, Config
from github import Github
import asyncio

class GithubInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=786128734626)  # Change the identifier to a unique integer
        self.config.register_global(github_token=None, text_template="GitHub Stars: {}")
        self.config.register_guild(channels={})
        self.task = None

        # Start the auto-updater task when the cog is loaded
        if not self.task or self.task.done():
            self.task = self.bot.loop.create_task(self.update_voice_channels())

    async def update_voice_channels(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            github_keys = await self.bot.get_shared_api_tokens("github")
            github_token = github_keys.get("api_key")

            if github_token is not None:
                # Create a GitHub instance
                github = Github(github_token)

                for guild_id, channel_info in (await self.config.all_guilds()).items():
                    guild = self.bot.get_guild(guild_id)
                    if guild is None:
                        continue

                    for channel_id, data in channel_info.get("channels", {}).items():
                        try:
                            # Get the repository
                            repo = github.get_repo(data["repo_link"])

                            # Get the number of stars
                            stars = repo.stargazers_count

                            # Get the configured text template
                            text_template = data.get("text_template", await self.config.text_template())

                            # Update the voice channel name
                            channel = guild.get_channel(channel_id)
                            if channel:
                                new_name = text_template.format(count=stars)
                                await channel.edit(name=new_name)
                        except Exception as e:
                            print(f"An error occurred: {str(e)}")

            await asyncio.sleep(30)

    @commands.command()
    async def githubinfo(self, ctx, *args):
        """
        Main command for GitHub info.

        Usage:
        [p]githubinfo stars <Repo link> - Manually query GitHub stars.
        [p]githubinfo channel <Channel-ID> <Repo Link> <Message> - Add a channel for GitHub stars updates.
        [p]githubinfo removechannel <ChannelID> - Remove a channel from GitHub stars updates.
        """
        if not args:
            return

        subcommand = args[0].lower()
        if subcommand == "stars":
            await self.github_stars(ctx, args[1])
        elif subcommand == "channel":
            await self.add_channel(ctx, args[1:])
        elif subcommand == "removechannel":
            await self.remove_channel(ctx, args[1])

    async def github_stars(self, ctx, repo_link):
        """Manually query GitHub stars."""
        github_keys = await self.bot.get_shared_api_tokens("github")
        github_token = github_keys.get("api_key")

        if github_token is None:
            return await ctx.send("The GitHub API token has not been set. Please ask a bot administrator to set it using `[p]set api github api_key,TOKEN`.")

        try:
            # Create a GitHub instance
            github = Github(github_token)

            # Get the repository
            repo = github.get_repo(repo_link)

            # Get the number of stars
            stars = repo.stargazers_count

            await ctx.send(f"Stars for {repo_link}: {stars}")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

    async def add_channel(self, ctx, args):
        """Add a channel for GitHub stars updates."""
        if len(args) < 3:
            return await ctx.send("Usage: `[p]githubinfo channel <Channel-ID> <Repo Link> <Message>`")

        channel_id, repo_link, message = args[0], args[1], " ".join(args[2:])

        try:
            channel_id = int(channel_id)
        except ValueError:
            return await ctx.send("Invalid Channel-ID. Please provide a valid numeric Channel-ID.")

        github_keys = await self.bot.get_shared_api_tokens("github")
        github_token = github_keys.get("api_key")

        if github_token is None:
            return await ctx.send("The GitHub API token has not been set. Please ask a bot administrator to set it using `[p]set api github api_key,TOKEN`.")

        try:
            # Create a GitHub instance
            github = Github(github_token)

            # Check if the repository exists
            github.get_repo(repo_link)

            # Save the channel info in guild configuration
            async with self.config.guild(ctx.guild).channels() as channels:
                channels[channel_id] = {"repo_link": repo_link, "text_template": message}
            await ctx.send(f"Channel with ID {channel_id} added for GitHub stars updates.")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

    async def remove_channel(self, ctx, channel_id):
        """Remove a channel from GitHub stars updates."""
        try:
            channel_id = int(channel_id)
        except ValueError:
            return await ctx.send("Invalid Channel-ID. Please provide a valid numeric Channel-ID.")

        async with self.config.guild(ctx.guild).channels() as channels:
            if channel_id in channels:
                del channels[channel_id]
                await ctx.send(f"Channel with ID {channel_id} removed from GitHub stars updates.")
            else:
                await ctx.send("Channel not found in the configuration.")

    def cog_unload(self):
        if self.task:
            self.task.cancel()

def setup(bot):
    bot.add_cog(GithubInfo(bot))
