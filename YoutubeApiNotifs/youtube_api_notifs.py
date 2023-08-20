import discord
from redbot.core import commands
import googleapiclient.discovery
from googleapiclient.errors import HttpError

class YoutubeApiNotifs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ytquery(self, ctx, channel_id: str):
        """Get the link to the newest video of a channel."""
        youtube_keys = await self.bot.get_shared_api_tokens("youtube")
        if "api_key" not in youtube_keys:
            await ctx.send("API key for YouTube not set. Use `[p]set api youtube api_key <key>` to set it.")
            return

        API_KEY = youtube_keys["api_key"]
        youtube = googleapiclient.discovery.build('youtube', 'v3', developerKey=API_KEY)

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
        except HttpError as e:
            if "API key expired" in str(e):
                await ctx.send("API key for YouTube has expired. Please renew the API key.")
            else:
                await ctx.send("An error occurred while fetching data from the YouTube API.")

def setup(bot):
    bot.add_cog(YoutubeApiNotifs(bot))
