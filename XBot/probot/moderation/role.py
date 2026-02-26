import discord
from discord import app_commands
from discord.ext import commands

class Role(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="role-add", description="إضافة رتبة لعضو")
    @app_commands.describe(member="العضو", role="الرتبة")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def role_add(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        await member.add_roles(role)
        embed = discord.Embed(title="✅ تمت إضافة الرتبة", color=discord.Color.green())
        embed.add_field(name="العضو", value=member.mention)
        embed.add_field(name="الرتبة", value=role.mention)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="role-remove", description="إزالة رتبة من عضو")
    @app_commands.describe(member="العضو", role="الرتبة")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def role_remove(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        await member.remove_roles(role)
        embed = discord.Embed(title="✅ تمت إزالة الرتبة", color=discord.Color.red())
        embed.add_field(name="العضو", value=member.mention)
        embed.add_field(name="الرتبة", value=role.mention)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Role(bot))
