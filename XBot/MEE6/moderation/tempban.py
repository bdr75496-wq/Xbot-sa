import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class TempBan(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="tempban", description="حظر مؤقت لعضو لمدة محددة (بالدقائق)")
    @app_commands.describe(member="العضو", duration="المدة بالدقائق", reason="السبب")
    @app_commands.checks.has_permissions(ban_members=True)
    async def tempban(self, interaction: discord.Interaction, member: discord.Member, duration: int, reason: str = "بدون سبب"):
        await member.ban(reason=reason)
        embed = discord.Embed(title="⏳ حظر مؤقت", color=discord.Color.orange())
        embed.add_field(name="العضو", value=member.mention)
        embed.add_field(name="المدة", value=f"{duration} دقيقة")
        embed.add_field(name="السبب", value=reason)
        embed.add_field(name="المشرف", value=interaction.user.mention)
        await interaction.response.send_message(embed=embed)
        await asyncio.sleep(duration * 60)
        await interaction.guild.unban(member)

async def setup(bot):
    await bot.add_cog(TempBan(bot))
