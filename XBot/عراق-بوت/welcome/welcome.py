import discord
from discord import app_commands
from discord.ext import commands
import json, os

def load_welcome():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists("data/welcome.json"):
        return {}
    with open("data/welcome.json", "r") as f:
        return json.load(f)

def save_welcome(data):
    with open("data/welcome.json", "w") as f:
        json.dump(data, f, indent=4)

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="welcome-setup", description="إعداد نظام الترحيب")
    @app_commands.describe(channel="قناة الترحيب", message="رسالة الترحيب (استخدم {user} و {server}")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def welcome_setup(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str = "مرحباً {user} في {server}!"):
        data = load_welcome()
        gid = str(interaction.guild.id)
        data[gid] = {"channel": channel.id, "message": message, "enabled": True}
        save_welcome(data)
        await interaction.response.send_message(f"✅ تم إعداد الترحيب في {channel.mention}")

    @app_commands.command(name="welcome-test", description="تجربة رسالة الترحيب")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def welcome_test(self, interaction: discord.Interaction):
        data = load_welcome()
        gid = str(interaction.guild.id)
        if gid not in data:
            return await interaction.response.send_message("❌ لم يتم إعداد الترحيب بعد!", ephemeral=True)
        channel = interaction.guild.get_channel(data[gid]["channel"])
        msg = data[gid]["message"].replace("{user}", interaction.user.mention).replace("{server}", interaction.guild.name)
        embed = discord.Embed(description=msg, color=discord.Color.green())
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await channel.send(embed=embed)
        await interaction.response.send_message("✅ تم إرسال رسالة تجريبية!", ephemeral=True)

    @app_commands.command(name="welcome-disable", description="تعطيل الترحيب")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def welcome_disable(self, interaction: discord.Interaction):
        data = load_welcome()
        gid = str(interaction.guild.id)
        if gid in data:
            data[gid]["enabled"] = False
            save_welcome(data)
        await interaction.response.send_message("✅ تم تعطيل الترحيب")

    @app_commands.command(name="goodbye-setup", description="إعداد رسالة المغادرة")
    @app_commands.describe(channel="القناة", message="الرسالة")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def goodbye_setup(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str = "وداعاً {user}!"):
        data = load_welcome()
        gid = str(interaction.guild.id)
        if gid not in data:
            data[gid] = {}
        data[gid]["goodbye_channel"] = channel.id
        data[gid]["goodbye_message"] = message
        data[gid]["goodbye_enabled"] = True
        save_welcome(data)
        await interaction.response.send_message(f"✅ تم إعداد رسالة المغادرة في {channel.mention}")

    @app_commands.command(name="goodbye-disable", description="تعطيل رسالة المغادرة")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def goodbye_disable(self, interaction: discord.Interaction):
        data = load_welcome()
        gid = str(interaction.guild.id)
        if gid in data:
            data[gid]["goodbye_enabled"] = False
            save_welcome(data)
        await interaction.response.send_message("✅ تم تعطيل رسالة المغادرة")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        data = load_welcome()
        gid = str(member.guild.id)
        if gid in data and data[gid].get("enabled"):
            channel = member.guild.get_channel(data[gid]["channel"])
            if channel:
                msg = data[gid]["message"].replace("{user}", member.mention).replace("{server}", member.guild.name)
                embed = discord.Embed(description=msg, color=discord.Color.green())
                embed.set_thumbnail(url=member.display_avatar.url)
                await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        data = load_welcome()
        gid = str(member.guild.id)
        if gid in data and data[gid].get("goodbye_enabled"):
            channel = member.guild.get_channel(data[gid]["goodbye_channel"])
            if channel:
                msg = data[gid]["goodbye_message"].replace("{user}", str(member)).replace("{server}", member.guild.name)
                embed = discord.Embed(description=msg, color=discord.Color.red())
                await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
