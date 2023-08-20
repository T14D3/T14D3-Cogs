from .youtube_api_notifs import YoutubeApiNotifs

def setup(bot):
    cog = YoutubeApiNotifs(bot)
    bot.add_cog(cog)
