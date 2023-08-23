import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
from rcon import Client

class RedCon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="send_rcon",
        description="Send an RCON command to a server",
        options=[
            create_option(
                name="ip",
                description="Server IP address",
                option_type=3,
                required=True
            ),
            create_option(
                name="port",
                description="Server port",
                option_type=4,
                required=True
            ),
            create_option(
                name="password",
                description="RCON password",
                option_type=3,
                required=True
            ),
            create_option(
                name="command",
                description="RCON command to send",
                option_type=3,
                required=True
            )
        ]
    )
    async def send_rcon(self, ctx: SlashContext, ip: str, port: int, password: str, command: str):
        try:
            with Client(ip, port, password) as client:
                response = client.execute(command)
            await ctx.send(f"RCON response:\n```\n{response}\n```")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

def setup(bot):
    bot.add_cog(RconCog(bot))
