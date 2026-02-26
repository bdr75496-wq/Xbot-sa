import discord
from discord.ext import commands
from discord import app_commands
import json, os, time
from collections import defaultdict
from datetime import timedelta

join_tracker = defaultdict(list)

def load_antiraid():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists("data/probot_antiraid.json"):
        return {}
    with open("data/probot_antiraid.json", "r") as f:
        return json.load(f)

def save_antiraid(data):
    with open("data/probot_antiraid.json", "w") as f:
        json.dump(data, f, indent=4)

class AntiRaid(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        data = load_antiraid()
        gid = str(member.guild.id)
        if not data.get(gid, {}).get("enabled"):
            return
        now = time.time()
        join_tracker[gid] = [t for t in join_tracker[gid] if now - t < 10]
        join_tracker[gid].append(now)
        threshold = data[gid].get("threshold", 5)
        if len(join_tracker[gid]) >= threshold:
            try:
                await member.timeout(timedelta(minutes=30))
                log_ch = member.guild.get_channel(data[gid].get("log_channel"))
                if log_ch:
                    embed = discord.Embed(title="🚨 تحذير ريد!", color=discord.Color.red())
                    embed.description = f"تم رصد {len(join_tracker[gid])} أعضاء انضموا في 10 ثواني!\n{member.mention} تم تقييده تلقائياً."
                    await log_ch.send(embed=embed)
            except:
                pass

    @app_commands.command(name="antiraid", description="إعداد الحماية من الريد")
    @app_commands.describe(status="تفعيل أو إيقاف", threshold="عدد الأعضاء المشبوه في 10 ثواني", log_channel="قناة السجل")
    @app_commands.choices(status=[
        app_commands.Choice(name="تفعيل", value="on"),
        app_commands.Choice(name="إيقاف", value="off")
    ])
    @app_commands.checks.has_permissions(administrator=True)
    async def antiraid(self, interaction: discord.Interaction, status: str, threshold: int = 5, log_channel: discord.TextChannel = None):
        data = load_antiraid()
        gid = str(interaction.guild.id)
        data[gid] = {
            "enabled": status == "on",
            "threshold": threshold,
            "log_channel": log_channel.id if log_channel else None
        }
        save_antiraid(data)
        state = "مفعّل ✅" if status == "on" else "موقوف ❌"
        embed = discord.Embed(title="🛡️ حماية الريد", color=discord.Color.blue())
        embed.add_field(name="الحالة", value=state)
        embed.add_field(name="الحد", value=f"{threshold} أعضاء / 10 ثواني")
        if log_channel:
            embed.add_field(name="قناة السجل", value=log_channel.mention)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="antiraid-status", description="عرض حالة حماية الريد")
    async def antiraid_status(self, interaction: discord.Interaction):
        data = load_antiraid()
        gid = str(interaction.guild.id)
        settings = data.get(gid, {})
        embed = discord.Embed(title="🛡️ حالة حماية الريد", color=discord.Color.blue())
        embed.add_field(name="الحالة", value="مفعّل ✅" if settings.get("enabled") else "موقوف ❌")
        embed.add_field(name="الحد", value=str(settings.get("threshold", 5)))
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(AntiRaid(bot))
