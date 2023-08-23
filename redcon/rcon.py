import discord
from redbot.core import commands, app_commands
from redbot.core.commands.context import ApplicationContext
from redbot.core.bot import Red
from redbot.core.ui import TextInput, NumberInput, CancellableModal

from rcon import Client
class RedCon(commands.Cog):
    def __init__(self, bot: Red):
        self.bot = bot
        self.tree = app_commands.CommandTree(self.bot)

    @self.tree.command(
        description="Execute RCON command"
    )
    async def rcon(self, ctx: ApplicationContext):
        # Send the modal with an instance of our RconModal class
        await ctx.send_modal(RconModal())

class RconModal(CancellableModal):
    def __init__(self):
        super().__init__(title="RCON Command")

        self.ip_input = TextInput(label="Server IP")
        self.port_input = NumberInput(label="Server Port")
        self.password_input = TextInput(label="RCON Password")
        self.command_input = TextInput(label="RCON Command")

        self.add_item(self.ip_input)
        self.add_item(self.port_input)
        self.add_item(self.password_input)
        self.add_item(self.command_input)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user == self.ctx.author

    async def on_confirm(self, interaction: discord.Interaction, values: dict):
        ip = values['ip_input']
        port = values['port_input']
        password = values['password_input']
        command = values['command_input']

        try:
            with Client(ip, port, password) as client:
                response = client.execute(command)
            await interaction.response.send_message(f'RCON response:\n```\n{response}\n```', ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)

def setup(bot: Red):
    bot.add_cog(RedCon(bot))
