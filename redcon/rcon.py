import discord
from discord import app_commands
from redbot.core import commands, app_commands
from rcon import Client


class RedCon(commands.Cog):
    def __init__(self, bot):

        self.bot = bot

        # self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        await self.tree.sync()

    @app_commands.command()
    async def run_rcon(self, interaction: discord.Interaction):
        await interaction.response.send_modal(InputModal())


class InputModal(discord.ui.Modal, title='Connection details'):
    ip = discord.ui.TextInput(
        label='IP',
        placeholder='Enter IP address',
    )
    port = discord.ui.TextInput(
        label='Port',
        placeholder='Enter remote port',
    )
    password = discord.ui.TextInput(
        label='Password',
        placeholder='Enter password',
    )
    command = discord.ui.TextInput(
        label='Command',
        placeholder='RCON-Command to execute',
    )

    #async def on_submit(self, interaction: discord.Interaction):
    #    await interaction.response.send_message(f'{self.ip.value} {self.port.value} {self.password.value} {self.command.value}', ephemeral=True)

    async def on_submit(self, interaction: discord.Interaction):
        ip_value = self.ip.value
        port_value = int(self.port.value)
        password_value = self.password.value
        command_value = self.command.value

        try:
            with Client(ip_value, port_value, passwd=password_value) as client:
                client.connect()  # Establish the RCON connection
                response = client.run(command_value)
            await interaction.response.send_message(f'RCON response:\n```\n{response}\n```', ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)


    

def setup(bot):
    bot.add_cog(RedCon(bot))
