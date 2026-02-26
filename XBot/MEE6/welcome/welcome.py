import discord
from discord.ext import commands
from discord import app_commands
import json, os

def load_welcome():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists("data/mee6_welcome.json"):
        return {}
    with open("data/mee6_welcome.json", "r") as f:
        return json.load(f)

def save_welcome(data):
    with open("data/mee6_welcome.json", "w") as f:
        json.dump(data, f, indent=4)

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        data = load_welcome()
        gid = str(member.guild.id)
        if gid not in data or not data[gid].get("enabled"):
            return
        channel = member.guild.get_channel(data[gid]["channel"])
        if channel:
            msg = data[gid].get("message", "مرحباً {user} في {server}!")
            msg = msg.replace("{user}", member.mention).replace("{server}", member.guild.name)
            embed = discord.Embed(description=msg, color=discord.Color.green())
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f"أنت العضو رقم {member.guild.member_count}")
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        data = load_welcome()
        gid = str(member.guild.id)
        if gid not in data or not data[gid].get("goodbye_enabled"):
            return
        channel = member.guild.get_channel(data[gid].get("goodbye_channel"))
        if channel:
            embed = discord.Embed(description=f"وداعاً **{member}**، نتمنى أن تعود قريباً! 👋", color=discord.Color.red())
            await channel.send(embed=embed)

    @app_commands.command(name="setwelcome", description="تحديد روم الترحيب")
    @app_commands.describe(channel="روم الترحيب", message="رسالة الترحيب (استخدم {user} و {server})")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setwelcome(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str = "مرحباً {user} في {server}! 🎉"):
        data = load_welcome()
        gid = str(interaction.guild.id)
        if gid not in data:
            data[gid] = {}
        data[gid]["channel"] = channel.id
        data[gid]["message"] = message
        data[gid]["enabled"] = True
        save_welcome(data)
        await interaction.response.send_message(f"✅ تم تعيين روم الترحيب على {channel.mention}")

    @app_commands.command(name="welcome-test", description="تجربة رسالة الترحيب")
    async def welcome_test(self, interaction: discord.Interaction):
        embed = discord.Embed(description=f"مرحباً {interaction.user.mention} في **{interaction.guild.name}**! 🎉\nهذا مثال على رسالة الترحيب.", color=discord.Color.green())
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="goodbye-test", description="تجربة رسالة المغادرة")
    async def goodbye_test(self, interaction: discord.Interaction):
        embed = discord.Embed(description=f"وداعاً **{interaction.user}**، نتمنى أن تعود قريباً! 👋", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
