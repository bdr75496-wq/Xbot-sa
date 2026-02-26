import discord
from discord import app_commands
from discord.ext import commands
from datetime import timedelta
import json, os

def load_warnings():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists("data/warnings.json"):
        return {}
    with open("data/warnings.json", "r") as f:
        return json.load(f)

def save_warnings(data):
    with open("data/warnings.json", "w") as f:
        json.dump(data, f, indent=4)

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="nickname", description="تغيير لقب عضو")
    @app_commands.describe(member="العضو", nickname="اللقب الجديد")
    @app_commands.checks.has_permissions(manage_nicknames=True)
    async def nickname(self, interaction: discord.Interaction, member: discord.Member, nickname: str):
        await member.edit(nick=nickname)
        await interaction.response.send_message(f"✅ تم تغيير لقب {member.mention} إلى **{nickname}**")

    @app_commands.command(name="reset-warnings", description="تصفير تحذيرات عضو")
    @app_commands.describe(member="العضو")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def reset_warnings(self, interaction: discord.Interaction, member: discord.Member):
        data = load_warnings()
        uid = str(member.id)
        if uid in data:
            data[uid] = []
            save_warnings(data)
        await interaction.response.send_message(f"✅ تم تصفير تحذيرات {member.mention}")

    @app_commands.command(name="ping", description="عرض سرعة البوت")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(title="🏓 بينج!", color=discord.Color.green())
        embed.add_field(name="السرعة", value=f"**{latency}ms**")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
