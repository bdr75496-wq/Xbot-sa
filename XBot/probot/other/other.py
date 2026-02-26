import discord
from discord import app_commands
from discord.ext import commands

class Other(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="embed", description="إنشاء embed مخصص")
    @app_commands.describe(title="العنوان", description="الوصف", color="اللون hex مثل ff0000")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def embed(self, interaction: discord.Interaction, title: str, description: str, color: str = "0099ff"):
        try:
            color_int = int(color.replace("#", ""), 16)
        except:
            color_int = 0x0099ff
        
        embed = discord.Embed(title=title, description=description, color=color_int)
        embed.set_footer(text=f"بواسطة {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="help", description="قائمة الأوامر")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📚 قائمة أوامر XBot", color=discord.Color.blue())
        embed.add_field(name="🛡️ الإدارة", value="`/ban` `/unban` `/kick` `/timeout` `/untimeout` `/warn` `/warnings` `/clear` `/slowmode` `/lock` `/unlock` `/role-add` `/role-remove`", inline=False)
        embed.add_field(name="📊 المستويات", value="`/rank` `/leaderboard` `/level`", inline=False)
        embed.add_field(name="👤 المعلومات", value="`/avatar` `/user` `/server` `/banner` `/botinfo`", inline=False)
        embed.add_field(name="🎁 القيف أواي", value="`/giveaway-create` `/giveaway-end` `/giveaway-reroll`", inline=False)
        embed.add_field(name="💬 أخرى", value="`/embed` `/help` `/report`", inline=False)
        embed.set_footer(text="XBot | مجاني 100% 🇵🇸")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="report", description="الإبلاغ عن عضو")
    @app_commands.describe(member="العضو", reason="السبب")
    async def report(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        embed = discord.Embed(title="🚨 بلاغ جديد", color=discord.Color.red())
        embed.add_field(name="المُبلَّغ عنه", value=member.mention)
        embed.add_field(name="السبب", value=reason)
        embed.add_field(name="المُبلِّغ", value=interaction.user.mention)
        embed.add_field(name="القناة", value=interaction.channel.mention)
        
        log_channel = discord.utils.get(interaction.guild.text_channels, name="logs")
        if log_channel:
            await log_channel.send(embed=embed)
        
        await interaction.response.send_message("✅ تم إرسال البلاغ للإدارة!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Other(bot))
