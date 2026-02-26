import discord
from discord.ext import commands
from discord import app_commands

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="userinfo", description="عرض معلومات عضو")
    @app_commands.describe(member="العضو (اختياري)")
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        embed = discord.Embed(title=f"👤 معلومات {member.display_name}", color=discord.Color.blue())
        embed.add_field(name="الاسم الكامل", value=str(member), inline=True)
        embed.add_field(name="الرقم التعريفي", value=str(member.id), inline=True)
        embed.add_field(name="انضم للسيرفر", value=member.joined_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="تاريخ إنشاء الحساب", value=member.created_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="الأدوار", value=", ".join([r.mention for r in member.roles[1:]]) or "لا يوجد", inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="serverinfo", description="عرض معلومات السيرفر")
    async def serverinfo(self, interaction: discord.Interaction):
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

    @app_commands.command(name="roleinfo", description="معلومات رتبة")
    @app_commands.describe(role="الرتبة")
    async def roleinfo(self, interaction: discord.Interaction, role: discord.Role):
        embed = discord.Embed(title=f"🎭 معلومات {role.name}", color=role.color)
        embed.add_field(name="الرقم التعريفي", value=str(role.id), inline=True)
        embed.add_field(name="اللون", value=str(role.color), inline=True)
        embed.add_field(name="عدد الأعضاء", value=str(len(role.members)), inline=True)
        embed.add_field(name="قابل للذكر", value="✅" if role.mentionable else "❌", inline=True)
        embed.add_field(name="تاريخ الإنشاء", value=role.created_at.strftime("%Y-%m-%d"), inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="avatar", description="عرض صورة عضو")
    @app_commands.describe(member="العضو (اختياري)")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        embed = discord.Embed(title=f"🖼️ صورة {member.display_name}", color=discord.Color.teal())
        embed.set_image(url=member.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="botinfo", description="معلومات البوت")
    async def botinfo(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🤖 معلومات XBot", color=discord.Color.blue())
        embed.add_field(name="الاسم", value=self.bot.user.name)
        embed.add_field(name="الرقم التعريفي", value=str(self.bot.user.id))
        embed.add_field(name="عدد السيرفرات", value=str(len(self.bot.guilds)))
        embed.add_field(name="المطور", value="XBot Team")
        embed.add_field(name="المكتبة", value="discord.py")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="help", description="عرض جميع الأوامر")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📚 قائمة أوامر Carl-bot", color=discord.Color.blue())
        embed.add_field(name="🛡️ الإدارة", value="`/ban` `/tempban` `/unban` `/kick` `/mute` `/unmute` `/warn` `/warnings` `/purge` `/slowmode` `/lock` `/unlock` `/nick` `/role`", inline=False)
        embed.add_field(name="⚙️ الأوتومود", value="`/automod` `/filter-add` `/filter-remove` `/antispam` `/antilink`", inline=False)
        embed.add_field(name="🎭 الرتب التفاعلية", value="`/rr-create` `/rr-add` `/rr-delete`", inline=False)
        embed.add_field(name="📊 المعلومات", value="`/userinfo` `/serverinfo` `/roleinfo` `/avatar` `/botinfo`", inline=False)
        embed.add_field(name="📜 السجلات", value="`/setlogs`", inline=False)
        embed.add_field(name="🎉 القيف أواي", value="`/gstart` `/gend` `/greroll`", inline=False)
        embed.add_field(name="🔧 التاقز", value="`/tag-create` `/tag-edit` `/tag-delete` `/tag`", inline=False)
        embed.add_field(name="⭐ ستاربورد", value="`/starboard-setup`", inline=False)
        embed.set_footer(text="XBot | مجاني 100%")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Info(bot))
