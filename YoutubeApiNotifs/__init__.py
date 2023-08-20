from .youtube_api_notifs import YoutubeApiNotifs

def setup(bot):
    bot.add_cog(YoutubeApiNotifs(bot))
