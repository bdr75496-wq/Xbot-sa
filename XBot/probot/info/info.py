import discord
from discord import app_commands
from discord.ext import commands

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="avatar", description="عرض صورة عضو")
    @app_commands.describe(member="العضو (اختياري)")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        embed = discord.Embed(title=f"🖼️ صورة {member.display_name}", color=discord.Color.blue())
        embed.set_image(url=member.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="user", description="معلومات عضو")
    @app_commands.describe(member="العضو (اختياري)")
    async def user(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        embed = discord.Embed(title=f"👤 معلومات {member.display_name}", color=discord.Color.blue())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="الاسم", value=str(member))
        embed.add_field(name="الID", value=member.id)
        embed.add_field(name="تاريخ الإنشاء", value=member.created_at.strftime("%Y-%m-%d"))
        embed.add_field(name="تاريخ الانضمام", value=member.joined_at.strftime("%Y-%m-%d"))
        embed.add_field(name="الرتب", value=" ".join([r.mention for r in member.roles[1:]]) or "لا يوجد")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="server", description="معلومات السيرفر")
    async def server(self, interaction: discord.Interaction):
        guild = interaction.guild
        embed = discord.Embed(title=f"🏠 معلومات {guild.name}", color=discord.Color.blue())
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="الID", value=guild.id)
        embed.add_field(name="المالك", value=guild.owner.mention)
        embed.add_field(name="الأعضاء", value=guild.member_count)
        embed.add_field(name="القنوات", value=len(guild.channels))
        embed.add_field(name="الرتب", value=len(guild.roles))
        embed.add_field(name="تاريخ الإنشاء", value=guild.created_at.strftime("%Y-%m-%d"))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="banner", description="عرض بانر عضو")
    @app_commands.describe(member="العضو (اختياري)")
    async def banner(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        user = await self.bot.fetch_user(member.id)
        if user.banner:
            embed = discord.Embed(title=f"🖼️ بانر {member.display_name}", color=discord.Color.blue())
            embed.set_image(url=user.banner.url)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ هذا العضو ليس لديه بانر!", ephemeral=True)

    @app_commands.command(name="botinfo", description="معلومات البوت")
    async def botinfo(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🤖 معلومات XBot", color=discord.Color.blue())
        embed.add_field(name="الاسم", value=self.bot.user.name)
        embed.add_field(name="الID", value=self.bot.user.id)
        embed.add_field(name="السيرفرات", value=len(self.bot.guilds))
        embed.add_field(name="المطور", value="Majed19108")
        embed.add_field(name="المكتبة", value="discord.py")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Info(bot))
