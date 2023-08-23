import discord
import discord.ext
from rcon import Client

class RedCon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def rcon(self, ctx: discord.ApplicationContext):
        await ctx.defer()

        modal = RconModal(title="RCON Command")
        await ctx.send_modal(modal)

class RconModal(ui.CancellableModal):
    def __init__(self, title):
        super().__init__(title=title)

        self.ip_input = ui.TextInput(label="Server IP")
        self.port_input = ui.NumberInput(label="Server Port")
        self.password_input = ui.TextInput(label="RCON Password")
        self.command_input = ui.TextInput(label="RCON Command")

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

def setup(bot):
    bot.add_cog(RedCon(bot))