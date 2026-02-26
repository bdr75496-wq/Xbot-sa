import discord
from discord import app_commands
from discord.ext import commands

class SlowmodeLock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="slowmode", description="تفعيل السلو مود")
    @app_commands.describe(seconds="المدة بالثواني (0 للإلغاء)")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def slowmode(self, interaction: discord.Interaction, seconds: int = 5):
        await interaction.channel.edit(slowmode_delay=seconds)
        if seconds == 0:
            await interaction.response.send_message("✅ تم إلغاء السلو مود")
        else:
            await interaction.response.send_message(f"⏱️ تم تفعيل السلو مود: {seconds} ثانية")

    @app_commands.command(name="lock", description="قفل القناة")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def lock(self, interaction: discord.Interaction):
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
        await interaction.response.send_message("🔒 تم قفل القناة")

    @app_commands.command(name="unlock", description="فتح القناة")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def unlock(self, interaction: discord.Interaction):
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
        await interaction.response.send_message("🔓 تم فتح القناة")

async def setup(bot):
    await bot.add_cog(SlowmodeLock(bot))
