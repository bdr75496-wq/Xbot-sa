import discord
from discord import app_commands
from discord.ext import commands
import json, os

warnings_file = "data/warnings.json"

def load_warnings():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(warnings_file):
        return {}
    with open(warnings_file, "r") as f:
        return json.load(f)

def save_warnings(data):
    with open(warnings_file, "w") as f:
        json.dump(data, f, indent=4)

class Warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="warn", description="تحذير عضو")
    @app_commands.describe(member="العضو", reason="السبب")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str = "بدون سبب"):
        data = load_warnings()
        uid = str(member.id)
        if uid not in data:
            data[uid] = []
        data[uid].append({"reason": reason, "by": str(interaction.user.id)})
        save_warnings(data)
        
        embed = discord.Embed(title="⚠️ تم التحذير", color=discord.Color.yellow())
        embed.add_field(name="العضو", value=member.mention)
        embed.add_field(name="السبب", value=reason)
        embed.add_field(name="عدد التحذيرات", value=len(data[uid]))
        embed.add_field(name="المشرف", value=interaction.user.mention)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="warnings", description="عرض تحذيرات عضو")
    @app_commands.describe(member="العضو")
    async def warnings(self, interaction: discord.Interaction, member: discord.Member):
        data = load_warnings()
        uid = str(member.id)
        warns = data.get(uid, [])
        
        embed = discord.Embed(title=f"⚠️ تحذيرات {member.display_name}", color=discord.Color.yellow())
        if not warns:
            embed.description = "لا توجد تحذيرات"
        else:
            for i, w in enumerate(warns, 1):
                embed.add_field(name=f"تحذير {i}", value=w["reason"], inline=False)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Warn(bot))
