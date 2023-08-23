import discord
from discord.ext import commands, ui
from rcon import Client

class RedCon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def rcon(self, ctx):
        view = RconView()
        await ctx.send("Please provide RCON details:", view=view, ephemeral=True)

class RconView(ui.View):
    def __init__(self):
        super().__init__()

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

    @ui.button(label="Execute RCON Command", style=discord.ButtonStyle.primary)
    async def execute_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        ip = self.ip_input.value
        port = self.port_input.value
        password = self.password_input.value
        command = self.command_input.value

        try:
            with Client(ip, port, password) as client:
                response = client.execute(command)
            await interaction.response.send_message(f'RCON response:\n```\n{response}\n```', ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)

def setup(bot):
    bot.add_cog(RedCon(bot))
