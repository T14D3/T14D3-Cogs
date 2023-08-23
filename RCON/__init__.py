from .rcon import RconCog

def setup(bot):
    bot.add_cog(RconCog(bot))
