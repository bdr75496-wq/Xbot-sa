import discord
from discord.ext import commands
from discord import app_commands
import json, os

def load_custom():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists("data/probot_custom.json"):
        return {}
    with open("data/probot_custom.json", "r") as f:
        return json.load(f)

def save_custom(data):
    with open("data/probot_custom.json", "w") as f:
        json.dump(data, f, indent=4)

class BotCustomizer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="set-prefix", description="تغيير بادئة البوت في سيرفرك")
    @app_commands.describe(prefix="البادئة الجديدة مثل ! أو . أو $")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_prefix(self, interaction: discord.Interaction, prefix: str):
        if len(prefix) > 3:
            return await interaction.response.send_message("❌ البادئة يجب أن تكون 3 حروف أو أقل!", ephemeral=True)
        data = load_custom()
        gid = str(interaction.guild.id)
        if gid not in data:
            data[gid] = {}
        data[gid]["prefix"] = prefix
        save_custom(data)
        embed = discord.Embed(title="⚙️ تم تغيير البادئة", color=discord.Color.blue())
        embed.add_field(name="البادئة الجديدة", value=f"`{prefix}`")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="set-welcome-image", description="تفعيل صورة ترحيب مخصصة")
    @app_commands.describe(channel="قناة الترحيب", background="رابط صورة الخلفية (اختياري)")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_welcome_image(self, interaction: discord.Interaction, channel: discord.TextChannel, background: str = None):
        data = load_custom()
        gid = str(interaction.guild.id)
        if gid not in data:
            data[gid] = {}
        data[gid]["welcome_channel"] = channel.id
        data[gid]["welcome_bg"] = background
        save_custom(data)
        embed = discord.Embed(title="🖼️ ترحيب بالصور", color=discord.Color.blue())
        embed.add_field(name="القناة", value=channel.mention)
        embed.add_field(name="الخلفية", value=background or "افتراضية")
        embed.description = "سيتم إرسال صورة ترحيب مخصصة لكل عضو جديد!"
        await interaction.response.send_message(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        data = load_custom()
        gid = str(member.guild.id)
        if not data.get(gid, {}).get("welcome_channel"):
            return
        ch = member.guild.get_channel(data[gid]["welcome_channel"])
        if not ch:
            return
        embed = discord.Embed(
            title=f"🎉 مرحباً {member.display_name}!",
            description=f"أهلاً بك في **{member.guild.name}** يا {member.mention}!\nأنت العضو رقم **{member.guild.member_count}**",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        if data[gid].get("welcome_bg"):
            embed.set_image(url=data[gid]["welcome_bg"])
        await ch.send(embed=embed)

    @app_commands.command(name="set-bot-name", description="تغيير اسم البوت في سيرفرك")
    @app_commands.describe(name="الاسم الجديد للبوت")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_bot_name(self, interaction: discord.Interaction, name: str):
        try:
            await interaction.guild.me.edit(nick=name)
            embed = discord.Embed(title="✏️ تم تغيير اسم البوت", color=discord.Color.blue())
            embed.add_field(name="الاسم الجديد", value=name)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"❌ حدث خطأ: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(BotCustomizer(bot))
