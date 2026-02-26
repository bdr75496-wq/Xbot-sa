import discord
from discord.ext import commands
from discord import app_commands

class Mute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="mute", description="كتم عضو كتابياً")
    @app_commands.describe(member="العضو", reason="السبب")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute(self, interaction: discord.Interaction, member: discord.Member, reason: str = "بدون سبب"):
        muted_role = discord.utils.get(interaction.guild.roles, name="مكتوم")
        if not muted_role:
            muted_role = await interaction.guild.create_role(name="مكتوم")
            for channel in interaction.guild.channels:
                await channel.set_permissions(muted_role, send_messages=False, speak=False)
        await member.add_roles(muted_role, reason=reason)
        embed = discord.Embed(title="🔇 تم الكتم", color=discord.Color.greyple())
        embed.add_field(name="العضو", value=member.mention)
        embed.add_field(name="السبب", value=reason)
        embed.add_field(name="المشرف", value=interaction.user.mention)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="unmute", description="إزالة الكتم عن عضو")
    @app_commands.describe(member="العضو")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        muted_role = discord.utils.get(interaction.guild.roles, name="مكتوم")
        if muted_role and muted_role in member.roles:
            await member.remove_roles(muted_role)
            embed = discord.Embed(title="🔊 تم إزالة الكتم", color=discord.Color.green())
            embed.add_field(name="العضو", value=member.mention)
            embed.add_field(name="المشرف", value=interaction.user.mention)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ العضو غير مكتوم!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Mute(bot))
