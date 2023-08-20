from .youtube_api_notifs import YoutubeApiNotifs

async def setup(bot):
    await bot.add_cog(YoutubeApiNotifs(bot))