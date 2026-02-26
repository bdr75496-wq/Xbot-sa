import discord
from discord import app_commands
from discord.ext import commands
from datetime import timedelta

class Timeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="timeout", description="كتم عضو مؤقتاً")
    @app_commands.describe(member="العضو", duration="المدة بالدقائق", reason="السبب")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, duration: int = 10, reason: str = "بدون سبب"):
        await member.timeout(timedelta(minutes=duration), reason=reason)
        
        embed = discord.Embed(title="🔇 تم الكتم", color=discord.Color.red())
        embed.add_field(name="العضو", value=member.mention)
        embed.add_field(name="المدة", value=f"{duration} دقيقة")
        embed.add_field(name="السبب", value=reason)
        embed.add_field(name="المشرف", value=interaction.user.mention)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="untimeout", description="رفع الكتم عن عضو")
    @app_commands.describe(member="العضو", reason="السبب")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def untimeout(self, interaction: discord.Interaction, member: discord.Member, reason: str = "بدون سبب"):
        await member.timeout(None, reason=reason)
        
        embed = discord.Embed(title="🔊 تم رفع الكتم", color=discord.Color.green())
        embed.add_field(name="العضو", value=member.mention)
        embed.add_field(name="المشرف", value=interaction.user.mention)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Timeout(bot))
