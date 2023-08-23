import discord
from discord import app_commands
from redbot.core import commands, app_commands

from rcon import Client


class RedCon(commands.Cog):
    def __init__(self, bot):
        super().__init__(bot=bot)

        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        await self.tree.sync()

    
class InputModal(discord.ui.Modal, title='Connection details'):
    input = discord.ui.TextInput(
        label='IP',
        placeholder='Enter IP address',
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Test-Response - {self.input.value}', ephemeral=True)

@app_commands.command()
async def run_rcon(interaction: discord.Interaction):
    await interaction.response.send_modal(InputModal())

    

def setup(bot):
    bot.add_cog(RedCon(bot))
