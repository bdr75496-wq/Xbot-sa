import discord
from discord import app_commands
from discord.ext import commands
import json, os, asyncio

def load_settings():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists("data/settings.json"):
        return {}
    with open("data/settings.json", "r") as f:
        return json.load(f)

def save_settings(data):
    with open("data/settings.json", "w") as f:
        json.dump(data, f, indent=4)

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="logs-setup", description="تحديد قناة اللوق")
    @app_commands.describe(channel="القناة")
    @app_commands.checks.has_permissions(administrator=True)
    async def logs_setup(self, interaction: discord.Interaction, channel: discord.TextChannel):
        data = load_settings()
        gid = str(interaction.guild.id)
        if gid not in data:
            data[gid] = {}
        data[gid]["logs_channel"] = channel.id
        save_settings(data)
        await interaction.response.send_message(f"✅ تم تحديد قناة اللوق: {channel.mention}")

    @app_commands.command(name="bot-settings", description="عرض إعدادات البوت")
    @app_commands.checks.has_permissions(administrator=True)
    async def bot_settings(self, interaction: discord.Interaction):
        data = load_settings()
        gid = str(interaction.guild.id)
        settings = data.get(gid, {})
        embed = discord.Embed(title="⚙️ إعدادات البوت", color=discord.Color.blue())
        embed.add_field(name="قناة اللوق", value=f"<#{settings.get('logs_channel', 'غير محدد')}>")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="maintenance-mode", description="تفعيل/تعطيل وضع الصيانة")
    @app_commands.describe(enabled="تفعيل أو تعطيل")
    @app_commands.checks.has_permissions(administrator=True)
    async def maintenance_mode(self, interaction: discord.Interaction, enabled: bool):
        data = load_settings()
        gid = str(interaction.guild.id)
        if gid not in data:
            data[gid] = {}
        data[gid]["maintenance"] = enabled
        save_settings(data)
        status = "🔧 تم تفعيل وضع الصيانة" if enabled else "✅ تم إلغاء وضع الصيانة"
        await interaction.response.send_message(status)

    @app_commands.command(name="reset-system", description="إعادة ضبط نظام كامل")
    @app_commands.describe(system="النظام (tickets/warnings/levels)")
    @app_commands.checks.has_permissions(administrator=True)
    async def reset_system(self, interaction: discord.Interaction, system: str):
        files = {
            "tickets": "data/tickets.json",
            "warnings": "data/warnings.json",
            "levels": "data/xp.json"
        }
        if system in files and os.path.exists(files[system]):
            os.remove(files[system])
            await interaction.response.send_message(f"✅ تم إعادة ضبط نظام **{system}**")
        else:
            await interaction.response.send_message("❌ النظام غير موجود!", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        data = load_settings()
        gid = str(message.guild.id)
        log_channel_id = data.get(gid, {}).get("logs_channel")
        if log_channel_id:
            log_channel = message.guild.get_channel(log_channel_id)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        data = load_settings()
        gid = str(guild.id)
        log_channel_id = data.get(gid, {}).get("logs_channel")
        if log_channel_id:
            channel = guild.get_channel(log_channel_id)
            if channel:
                embed = discord.Embed(title="🔨 تم حظر عضو", color=discord.Color.red())
                embed.add_field(name="العضو", value=str(user))
                await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        data = load_settings()
        gid = str(member.guild.id)
        log_channel_id = data.get(gid, {}).get("logs_channel")
        if log_channel_id:
            channel = member.guild.get_channel(log_channel_id)
            if channel:
                embed = discord.Embed(title="👢 غادر عضو", color=discord.Color.orange())
                embed.add_field(name="العضو", value=str(member))
                await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Admin(bot))
