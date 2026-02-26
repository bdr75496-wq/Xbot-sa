import discord
from discord.ext import commands
from discord import app_commands

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="user-info", description="عرض معلومات عضو")
    @app_commands.describe(member="العضو (اختياري)")
    async def user_info(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        embed = discord.Embed(title=f"👤 معلومات {member.display_name}", color=discord.Color.blue())
        embed.add_field(name="الاسم الكامل", value=str(member), inline=True)
        embed.add_field(name="الرقم التعريفي", value=str(member.id), inline=True)
        embed.add_field(name="انضم للسيرفر", value=member.joined_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="تاريخ إنشاء الحساب", value=member.created_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="الأدوار", value=", ".join([r.mention for r in member.roles[1:]]) or "لا يوجد", inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="server-info", description="عرض معلومات السيرفر")
    async def server_info(self, interaction: discord.Interaction):
        guild = interaction.guild
        embed = discord.Embed(title=f"🏠 معلومات سيرفر {guild.name}", color=discord.Color.purple())
        embed.add_field(name="عدد الأعضاء", value=str(guild.member_count), inline=True)
        embed.add_field(name="عدد الرومات", value=str(len(guild.channels)), inline=True)
        embed.add_field(name="عدد الأدوار", value=str(len(guild.roles)), inline=True)
        embed.add_field(name="تاريخ الإنشاء", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="مالك السيرفر", value=str(guild.owner), inline=True)
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="avatar", description="عرض صورة عضو")
    @app_commands.describe(member="العضو (اختياري)")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        embed = discord.Embed(title=f"🖼️ صورة {member.display_name}", color=discord.Color.teal())
        embed.set_image(url=member.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="poll", description="إنشاء تصويت")
    @app_commands.describe(question="سؤال التصويت")
    async def poll(self, interaction: discord.Interaction, question: str):
        embed = discord.Embed(title="📊 تصويت جديد", description=question, color=discord.Color.blue())
        embed.set_footer(text=f"بواسطة {interaction.user.display_name}")
        msg = await interaction.channel.send(embed=embed)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")
        await interaction.response.send_message("✅ تم إنشاء التصويت!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Info(bot))
