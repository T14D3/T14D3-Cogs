import discord
from redbot.core import commands, Config
import googleapiclient.discovery

class YoutubeApiNotifs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier="youtube_api_notifs")
        default_guild_settings = {
            "api_key": ""
        }
        self.config.register_guild(**default_guild_settings)

    @commands.command()
    async def setapikey(self, ctx, api_key: str):
        """Set the YouTube API key for this cog."""
        await self.config.guild(ctx.guild).api_key.set(api_key)
        await ctx.message.delete()
        await ctx.send("YouTube API key set successfully!", delete_after=5)

    @commands.command()
    async def ytquery(self, ctx, channel_id: str):
        """Get the link to the newest video of a channel."""
        api_key = await self.config.guild(ctx.guild).api_key()
        if not api_key:
            await ctx.send("The YouTube API key has not been set. Use `[p]setapikey <api_key>` to set it.")
            return
        
        youtube = googleapiclient.discovery.build('youtube', 'v3', developerKey=api_key)

        try:
            response = youtube.search().list(
                part='id',
                channelId=channel_id,
                order='date',
                type='video',
                maxResults=1
            ).execute()

            if 'items' in response:
                video_id = response['items'][0]['id']['videoId']
                video_link = f"https://www.youtube.com/watch?v={video_id}"
                await ctx.send(f"Newest Video Link: {video_link}")
            else:
                await ctx.send("No videos found on the channel.")
        except googleapiclient.errors.HttpError as e:
            if "API key expired" in str(e):
                await ctx.send("API key for YouTube has expired. Please renew the API key.")
            else:
                await ctx.send("An error occurred while fetching data from the YouTube API.")

def setup(bot):
    bot.add_cog(YoutubeApiNotifs(bot))
