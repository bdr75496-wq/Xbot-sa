import discord
from discord.ext import commands
from discord import app_commands
import json, os, asyncio, random

ARABIC_SONGS = [
    {"title": "بشرة خير", "artist": "حسين الجسمي", "hint": "أغنية إماراتية شهيرة 🇦🇪"},
    {"title": "اه وارت عيني", "artist": "محمد عبده", "hint": "أغنية سعودية كلاسيكية 🇸🇦"},
    {"title": "يا ليلة العيد", "artist": "فيروز", "hint": "أغنية لبنانية للأعياد 🇱🇧"},
    {"title": "امل حياتي", "artist": "وردة الجزائرية", "hint": "أغنية مصرية جميلة 🇪🇬"},
    {"title": "سيدي منصور", "artist": "لطفي بوشناق", "hint": "أغنية تونسية 🇹🇳"},
    {"title": "يا طير الطاير", "artist": "عبادي الجوهر", "hint": "أغنية خليجية 🇸🇦"},
    {"title": "ست الحبايب", "artist": "فيروز", "hint": "أغنية لبنانية للأمهات 🇱🇧"},
    {"title": "انا عندي حنين", "artist": "كاظم الساهر", "hint": "أغنية عراقية رومانسية 🇮🇶"},
    {"title": "يا مسافر وحدك", "artist": "محمد عبده", "hint": "أغنية سعودية كلاسيكية 🇸🇦"},
    {"title": "الليالي", "artist": "وائل كفوري", "hint": "أغنية لبنانية 🇱🇧"},
]

active_quizzes = {}

class MusicQuiz(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="music-quiz", description="ابدأ مسابقة موسيقية عربية")
    @app_commands.describe(rounds="عدد الجولات (max 10)", time_per_round="الوقت لكل جولة بالثواني")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def music_quiz(self, interaction: discord.Interaction, rounds: int = 5, time_per_round: int = 30):
        if rounds > 10:
            return await interaction.response.send_message("❌ الحد الأقصى 10 جولات!", ephemeral=True)
        gid = str(interaction.guild.id)
        if gid in active_quizzes:
            return await interaction.response.send_message("❌ يوجد مسابقة نشطة في هذا السيرفر!", ephemeral=True)
        active_quizzes[gid] = {"scores": {}, "active": True}
        embed = discord.Embed(title="🎵 مسابقة موسيقية!", color=discord.Color.gold())
        embed.description = f"**{rounds}** جولات | **{time_per_round}** ثانية لكل جولة\nاكتب اسم الأغنية أو الفنان!"
        await interaction.response.send_message(embed=embed)
        songs = random.sample(ARABIC_SONGS, min(rounds, len(ARABIC_SONGS)))
        for i, song in enumerate(songs, 1):
            if not active_quizzes.get(gid, {}).get("active"):
                break
            q_embed = discord.Embed(title=f"🎵 جولة {i}/{len(songs)}", color=discord.Color.blue())
            q_embed.description = f"**تلميح:** {song['hint']}\nمن هو الفنان أو ما اسم الأغنية؟"
            q_embed.set_footer(text=f"لديك {time_per_round} ثانية ⏱️")
            await interaction.channel.send(embed=q_embed)
            answered = False
            try:
                while not answered:
                    msg = await self.bot.wait_for("message", timeout=time_per_round, check=lambda m: m.channel == interaction.channel and not m.bot)
                    if song["title"].lower() in msg.content.lower() or song["artist"].lower() in msg.content.lower():
                        uid = str(msg.author.id)
                        active_quizzes[gid]["scores"][uid] = active_quizzes[gid]["scores"].get(uid, 0) + 1
                        await interaction.channel.send(f"✅ {msg.author.mention} أجاب صح! **{song['title']}** - {song['artist']} 🎉")
                        answered = True
            except asyncio.TimeoutError:
                await interaction.channel.send(f"⏰ انتهى الوقت! الإجابة: **{song['title']}** - {song['artist']}")
            await asyncio.sleep(3)
        scores = active_quizzes.pop(gid, {}).get("scores", {})
        result_embed = discord.Embed(title="🏆 نتائج المسابقة", color=discord.Color.gold())
        if scores:
            medals = ["🥇", "🥈", "🥉"]
            for i, (uid, score) in enumerate(sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]):
                try:
                    user = await self.bot.fetch_user(int(uid))
                    medal = medals[i] if i < 3 else f"{i+1}."
                    result_embed.add_field(name=f"{medal} {user.display_name}", value=f"{score} نقطة", inline=False)
                except:
                    pass
        else:
            result_embed.description = "لم يجب أحد بشكل صحيح 😢"
        await interaction.channel.send(embed=result_embed)

    @app_commands.command(name="stop-quiz", description="إيقاف المسابقة الحالية")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def stop_quiz(self, interaction: discord.Interaction):
        gid = str(interaction.guild.id)
        if gid in active_quizzes:
            active_quizzes[gid]["active"] = False
            await interaction.response.send_message("✅ تم إيقاف المسابقة.")
        else:
            await interaction.response.send_message("❌ لا توجد مسابقة نشطة!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(MusicQuiz(bot))
