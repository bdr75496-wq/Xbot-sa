import discord
from discord.ext import commands
from discord import app_commands

class Unban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="unban", description="فك حظر عضو")
    @app_commands.describe(user_id="الرقم التعريفي للعضو المراد فك حظره", reason="السبب")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user_id: str, reason: str = "بدون سبب"):
        try:
            user = await self.bot.fetch_user(int(user_id))
            await interaction.guild.unban(user, reason=reason)
            embed = discord.Embed(title="✅ تم فك الحظر", color=discord.Color.green())
            embed.add_field(name="العضو", value=str(user))
            embed.add_field(name="السبب", value=reason)
            embed.add_field(name="المشرف", value=interaction.user.mention)
            await interaction.response.send_message(embed=embed)
        except:
            await interaction.response.send_message("❌ لم يتم العثور على العضو أو غير محظور!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Unban(bot))
