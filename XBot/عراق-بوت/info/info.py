import discord
from discord import app_commands
from discord.ext import commands

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="role-info", description="معلومات رتبة")
    @app_commands.describe(role="الرتبة")
    async def role_info(self, interaction: discord.Interaction, role: discord.Role):
        embed = discord.Embed(title=f"🎭 معلومات {role.name}", color=role.color)
        embed.add_field(name="الID", value=role.id)
        embed.add_field(name="اللون", value=str(role.color))
        embed.add_field(name="الأعضاء", value=len(role.members))
        embed.add_field(name="القابل للذكر", value="✅" if role.mentionable else "❌")
        embed.add_field(name="تاريخ الإنشاء", value=role.created_at.strftime("%Y-%m-%d"))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="emoji-add", description="إضافة إيموجي")
    @app_commands.describe(name="اسم الإيموجي", url="رابط الصورة")
    @app_commands.checks.has_permissions(manage_emojis=True)
    async def emoji_add(self, interaction: discord.Interaction, name: str, url: str):
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                image = await resp.read()
        emoji = await interaction.guild.create_custom_emoji(name=name, image=image)
        await interaction.response.send_message(f"✅ تم إضافة الإيموجي {emoji}")

    @app_commands.command(name="emoji-remove", description="حذف إيموجي")
    @app_commands.describe(emoji_name="اسم الإيموجي")
    @app_commands.checks.has_permissions(manage_emojis=True)
    async def emoji_remove(self, interaction: discord.Interaction, emoji_name: str):
        emoji = discord.utils.get(interaction.guild.emojis, name=emoji_name)
        if emoji:
            await emoji.delete()
            await interaction.response.send_message(f"✅ تم حذف الإيموجي **{emoji_name}**")
        else:
            await interaction.response.send_message("❌ الإيموجي غير موجود!", ephemeral=True)

    @app_commands.command(name="emoji-list", description="عرض جميع الإيموجيات")
    async def emoji_list(self, interaction: discord.Interaction):
        emojis = interaction.guild.emojis
        if not emojis:
            return await interaction.response.send_message("❌ لا توجد إيموجيات مخصصة!")
        embed = discord.Embed(title="😀 الإيموجيات المخصصة", color=discord.Color.blue())
        emoji_list = " ".join([str(e) for e in emojis])
        embed.description = emoji_list
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Info(bot))
