import discord
from discord import app_commands
from discord.ext import commands

class Clear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="clear", description="مسح رسائل من القناة")
    @app_commands.describe(amount="عدد الرسائل")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int = 10):
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"🗑️ تم مسح {len(deleted)} رسالة", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Clear(bot))
