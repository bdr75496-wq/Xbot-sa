import discord
from discord import app_commands
from discord.ext import commands
import json, os

def load_xp():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists("data/xp.json"):
        return {}
    with open("data/xp.json", "r") as f:
        return json.load(f)

def save_xp(data):
    with open("data/xp.json", "w") as f:
        json.dump(data, f, indent=4)

class Rank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="rank", description="عرض رتبتك ومستواك")
    @app_commands.describe(member="العضو (اختياري)")
    async def rank(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        data = load_xp()
        uid = str(member.id)
        if uid not in data:
            data[uid] = {"xp": 0, "level": 1}
        
        xp = data[uid]["xp"]
        level = data[uid]["level"]
        needed = level * 100
        
        embed = discord.Embed(title=f"📊 رتبة {member.display_name}", color=discord.Color.blue())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="المستوى", value=f"**{level}**")
        embed.add_field(name="الخبرة", value=f"**{xp} / {needed}**")
        
        bar_filled = int((xp / needed) * 10)
        bar = "🟦" * bar_filled + "⬜" * (10 - bar_filled)
        embed.add_field(name="التقدم", value=bar, inline=False)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leaderboard", description="عرض لوحة المتصدرين")
    async def leaderboard(self, interaction: discord.Interaction):
        data = load_xp()
        sorted_data = sorted(data.items(), key=lambda x: (x[1]["level"], x[1]["xp"]), reverse=True)
        
        embed = discord.Embed(title="🏆 لوحة المتصدرين", color=discord.Color.gold())
        
        medals = ["🥇", "🥈", "🥉"]
        for i, (uid, stats) in enumerate(sorted_data[:10]):
            try:
                user = await self.bot.fetch_user(int(uid))
                medal = medals[i] if i < 3 else f"`{i+1}.`"
                embed.add_field(
                    name=f"{medal} {user.display_name}",
                    value=f"المستوى: **{stats['level']}** | الخبرة: **{stats['xp']}**",
                    inline=False
                )
            except:
                pass
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="level", description="عرض المستوى")
    @app_commands.describe(member="العضو (اختياري)")
    async def level(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        data = load_xp()
        uid = str(member.id)
        if uid not in data:
            data[uid] = {"xp": 0, "level": 1}
        
        embed = discord.Embed(title=f"⭐ مستوى {member.display_name}", color=discord.Color.blue())
        embed.add_field(name="المستوى الحالي", value=f"**{data[uid]['level']}**")
        
        await interaction.response.send_message(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        data = load_xp()
        uid = str(message.author.id)
        if uid not in data:
            data[uid] = {"xp": 0, "level": 1}
        
        data[uid]["xp"] += 10
        if data[uid]["xp"] >= data[uid]["level"] * 100:
            data[uid]["level"] += 1
            data[uid]["xp"] = 0
            await message.channel.send(f"🎉 {message.author.mention} وصل للمستوى **{data[uid]['level']}**!")
        
        save_xp(data)

async def setup(bot):
    await bot.add_cog(Rank(bot))
