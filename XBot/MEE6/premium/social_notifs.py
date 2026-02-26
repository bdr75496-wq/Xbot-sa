import discord
from discord.ext import commands
from discord import app_commands
import json, os

def load_notifs():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists("data/mee6_notifs.json"):
        return {}
    with open("data/mee6_notifs.json", "r") as f:
        return json.load(f)

def save_notifs(data):
    with open("data/mee6_notifs.json", "w") as f:
        json.dump(data, f, indent=4)

class SocialNotifications(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="youtube-notif", description="تنبيه عند نشر فيديو يوتيوب جديد")
    @app_commands.describe(channel_id="ID قناة اليوتيوب", discord_channel="قناة الديسكورد للإشعارات", message="الرسالة المخصصة")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def youtube_notif(self, interaction: discord.Interaction, channel_id: str, discord_channel: discord.TextChannel, message: str = "🎥 فيديو جديد نُشر!"):
        data = load_notifs()
        gid = str(interaction.guild.id)
        if gid not in data: data[gid] = {}
        if "youtube" not in data[gid]: data[gid]["youtube"] = []
        data[gid]["youtube"].append({"channel_id": channel_id, "discord_channel": discord_channel.id, "message": message})
        save_notifs(data)
        embed = discord.Embed(title="▶️ تم إضافة تنبيه اليوتيوب", color=discord.Color.red())
        embed.add_field(name="قناة اليوتيوب", value=channel_id)
        embed.add_field(name="قناة الإشعارات", value=discord_channel.mention)
        embed.add_field(name="الرسالة", value=message)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="twitch-notif", description="تنبيه عند بث مباشر على تويتش")
    @app_commands.describe(twitch_user="اسم المستخدم على تويتش", discord_channel="قناة الإشعارات", message="رسالة مخصصة")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def twitch_notif(self, interaction: discord.Interaction, twitch_user: str, discord_channel: discord.TextChannel, message: str = "🔴 البث المباشر بدأ!"):
        data = load_notifs()
        gid = str(interaction.guild.id)
        if gid not in data: data[gid] = {}
        if "twitch" not in data[gid]: data[gid]["twitch"] = []
        data[gid]["twitch"].append({"user": twitch_user, "discord_channel": discord_channel.id, "message": message})
        save_notifs(data)
        embed = discord.Embed(title="🟣 تم إضافة تنبيه تويتش", color=discord.Color.purple())
        embed.add_field(name="المستخدم", value=twitch_user)
        embed.add_field(name="قناة الإشعارات", value=discord_channel.mention)
        embed.add_field(name="الرسالة", value=message)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="notif-list", description="عرض جميع تنبيهات الشبكات الاجتماعية")
    async def notif_list(self, interaction: discord.Interaction):
        data = load_notifs()
        settings = data.get(str(interaction.guild.id), {})
        embed = discord.Embed(title="🔔 قائمة التنبيهات", color=discord.Color.blue())
        yt = settings.get("youtube", [])
        tw = settings.get("twitch", [])
        if yt:
            embed.add_field(name="▶️ يوتيوب", value="\n".join([f"• {y['channel_id']}" for y in yt]), inline=False)
        if tw:
            embed.add_field(name="🟣 تويتش", value="\n".join([f"• {t['user']}" for t in tw]), inline=False)
        if not yt and not tw:
            embed.description = "لا توجد تنبيهات مضافة بعد."
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="notif-remove", description="حذف تنبيه")
    @app_commands.describe(platform="المنصة", name="اسم القناة أو المستخدم")
    @app_commands.choices(platform=[
        app_commands.Choice(name="يوتيوب", value="youtube"),
        app_commands.Choice(name="تويتش", value="twitch"),
    ])
    @app_commands.checks.has_permissions(manage_guild=True)
    async def notif_remove(self, interaction: discord.Interaction, platform: str, name: str):
        data = load_notifs()
        gid = str(interaction.guild.id)
        if gid in data and platform in data[gid]:
            key = "channel_id" if platform == "youtube" else "user"
            data[gid][platform] = [x for x in data[gid][platform] if x.get(key) != name]
            save_notifs(data)
            await interaction.response.send_message(f"✅ تم حذف تنبيه **{name}**")
        else:
            await interaction.response.send_message("❌ لم يتم العثور على التنبيه!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SocialNotifications(bot))
