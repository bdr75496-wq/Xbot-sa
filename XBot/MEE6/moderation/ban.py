import discord
from discord.ext import commands
from discord import app_commands

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ban", description="حظر عضو من السيرفر")
    @app_commands.describe(member="العضو المراد حظره", reason="سبب الحظر")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "بدون سبب"):
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("❌ لا تستطيع حظر شخص رتبته أعلى منك!", ephemeral=True)
        await member.ban(reason=reason)
        embed = discord.Embed(title="🔨 تم الحظر", color=discord.Color.red())
        embed.add_field(name="العضو", value=member.mention)
        embed.add_field(name="السبب", value=reason)
        embed.add_field(name="المشرف", value=interaction.user.mention)
        embed.set_footer(text=f"الرقم التعريفي: {member.id}")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Ban(bot))
