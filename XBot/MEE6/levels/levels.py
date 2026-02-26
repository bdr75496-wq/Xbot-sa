import discord
from discord.ext import commands
from discord import app_commands
import json, os, random

LEVELS_FILE = "data/levels.json"

def load_data():
    if not os.path.exists("data"):
        os.makedirs("data")
    if os.path.exists(LEVELS_FILE):
        with open(LEVELS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(LEVELS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def xp_needed(level):
    return 5 * (level ** 2) + 50 * level + 100

class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        gid = str(message.guild.id)
        uid = str(message.author.id)
        if gid not in self.data:
            self.data[gid] = {}
        if uid not in self.data[gid]:
            self.data[gid][uid] = {"xp": 0, "level": 0}

        self.data[gid][uid]["xp"] += random.randint(15, 25)
        current_level = self.data[gid][uid]["level"]

        if self.data[gid][uid]["xp"] >= xp_needed(current_level):
            self.data[gid][uid]["xp"] -= xp_needed(current_level)
            self.data[gid][uid]["level"] += 1
            new_level = self.data[gid][uid]["level"]
            embed = discord.Embed(
                title="🎉 ارتقيت مستوى!",
                description=f"مبروك {message.author.mention}! وصلت للمستوى **{new_level}** 🚀",
                color=discord.Color.gold()
            )
            await message.channel.send(embed=embed)
        save_data(self.data)

    @app_commands.command(name="rank", description="عرض مستواك ونقاطك")
    @app_commands.describe(member="العضو (اختياري)")
    async def rank(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        gid = str(interaction.guild.id)
        uid = str(member.id)
        user_data = self.data.get(gid, {}).get(uid, {"xp": 0, "level": 0})
        level = user_data["level"]
        xp = user_data["xp"]
        needed = xp_needed(level)
        bar_filled = int((xp / needed) * 10) if needed > 0 else 0
        bar = "🟦" * bar_filled + "⬜" * (10 - bar_filled)
        embed = discord.Embed(title=f"📊 رتبة {member.display_name}", color=discord.Color.blue())
        embed.add_field(name="المستوى", value=f"**{level}**", inline=True)
        embed.add_field(name="الخبرة", value=f"**{xp} / {needed}**", inline=True)
        embed.add_field(name="التقدم", value=bar, inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leaderboard", description="لوحة المتصدرين")
    async def leaderboard(self, interaction: discord.Interaction):
        gid = str(interaction.guild.id)
        guild_data = self.data.get(gid, {})
        sorted_users = sorted(guild_data.items(), key=lambda x: (x[1]["level"], x[1]["xp"]), reverse=True)
        embed = discord.Embed(title="🏆 لوحة المتصدرين", color=discord.Color.gold())
        medals = ["🥇", "🥈", "🥉"]
        for i, (uid, udata) in enumerate(sorted_users[:10], 1):
            try:
                user = await self.bot.fetch_user(int(uid))
                medal = medals[i-1] if i <= 3 else f"`{i}.`"
                embed.add_field(name=f"{medal} {user.display_name}", value=f"المستوى: **{udata['level']}** | الخبرة: **{udata['xp']}**", inline=False)
            except:
                pass
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Levels(bot))
