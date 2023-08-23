from .rcon import RedCon

async def setup(bot):
    await bot.add_cog(RedCon(bot))

    bot.tree.add_command(run_rcon)

async def teardown(bot):
    bot.tree.remove_command(run_rcon)
