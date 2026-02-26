import discord
from discord.ext import commands
from discord import app_commands
import re, time, json, os
from collections import defaultdict

spam_tracker = defaultdict(list)

def load_filter():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists("data/carlbot_filter.json"):
        return {}
    with open("data/carlbot_filter.json", "r") as f:
        return json.load(f)

def save_filter(data):
    with open("data/carlbot_filter.json", "w") as f:
        json.dump(data, f, indent=4)

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        data = load_filter()
        gid = str(message.guild.id)
        if gid not in data:
            return

        if not message.author.guild_permissions.manage_messages:
            # فلتر الروابط
            if data[gid].get("anti_link"):
                if re.search(r'https?://\S+|discord\.gg/\S+', message.content):
                    await message.delete()
                    await message.channel.send(f"🚫 {message.author.mention} ممنوع إرسال الروابط!", delete_after=4)
                    return

            # فلتر الكلمات
            for word in data[gid].get("bad_words", []):
                if word.strip().lower() in message.content.lower():
                    await message.delete()
                    await message.channel.send(f"🚫 {message.author.mention} رسالتك تحتوي على كلمة محظورة!", delete_after=4)
                    return

            # فلتر السبام
            if data[gid].get("anti_spam"):
                uid = message.author.id
                now = time.time()
                spam_tracker[uid] = [t for t in spam_tracker[uid] if now - t < 5]
                spam_tracker[uid].append(now)
                if len(spam_tracker[uid]) >= 5:
                    await message.delete()
                    await message.channel.send(f"🚫 {message.author.mention} لا تقم بالسبام!", delete_after=4)

    @app_commands.command(name="automod", description="عرض حالة أنظمة الحماية")
    async def automod(self, interaction: discord.Interaction):
        data = load_filter()
        gid = str(interaction.guild.id)
        settings = data.get(gid, {})
        embed = discord.Embed(title="🛡️ حالة أنظمة الحماية", color=discord.Color.blue())
        embed.add_field(name="فلتر الروابط", value="✅ مفعّل" if settings.get("anti_link") else "❌ موقوف", inline=True)
        embed.add_field(name="فلتر السبام", value="✅ مفعّل" if settings.get("anti_spam") else "❌ موقوف", inline=True)
        embed.add_field(name="الكلمات المحظورة", value=str(len(settings.get("bad_words", []))) + " كلمة", inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="filter-add", description="إضافة كلمة للقائمة السوداء")
    @app_commands.describe(word="الكلمة المحظورة")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def filter_add(self, interaction: discord.Interaction, word: str):
        data = load_filter()
        gid = str(interaction.guild.id)
        if gid not in data:
            data[gid] = {}
        if "bad_words" not in data[gid]:
            data[gid]["bad_words"] = []
        if word.lower() not in data[gid]["bad_words"]:
            data[gid]["bad_words"].append(word.lower())
        save_filter(data)
        await interaction.response.send_message(f"✅ تم إضافة الكلمة المحظورة: **{word}**")

    @app_commands.command(name="filter-remove", description="إزالة كلمة من الفلتر")
    @app_commands.describe(word="الكلمة")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def filter_remove(self, interaction: discord.Interaction, word: str):
        data = load_filter()
        gid = str(interaction.guild.id)
        if gid in data and word.lower() in data[gid].get("bad_words", []):
            data[gid]["bad_words"].remove(word.lower())
            save_filter(data)
            await interaction.response.send_message(f"✅ تم إزالة الكلمة: **{word}**")
        else:
            await interaction.response.send_message("❌ الكلمة غير موجودة في الفلتر!", ephemeral=True)

    @app_commands.command(name="antispam", description="تفعيل/إيقاف مانع السبام")
    @app_commands.choices(status=[app_commands.Choice(name="تفعيل", value="on"), app_commands.Choice(name="إيقاف", value="off")])
    @app_commands.checks.has_permissions(manage_guild=True)
    async def antispam(self, interaction: discord.Interaction, status: str):
        data = load_filter()
        gid = str(interaction.guild.id)
        if gid not in data:
            data[gid] = {}
        data[gid]["anti_spam"] = (status == "on")
        save_filter(data)
        state = "مفعّل ✅" if status == "on" else "موقوف ❌"
        await interaction.response.send_message(f"🛡️ مانع السبام: **{state}**")

    @app_commands.command(name="antilink", description="تفعيل/إيقاف مانع الروابط")
    @app_commands.choices(status=[app_commands.Choice(name="تفعيل", value="on"), app_commands.Choice(name="إيقاف", value="off")])
    @app_commands.checks.has_permissions(manage_guild=True)
    async def antilink(self, interaction: discord.Interaction, status: str):
        data = load_filter()
        gid = str(interaction.guild.id)
        if gid not in data:
            data[gid] = {}
        data[gid]["anti_link"] = (status == "on")
        save_filter(data)
        state = "مفعّل ✅" if status == "on" else "موقوف ❌"
        await interaction.response.send_message(f"🔗 مانع الروابط: **{state}**")

async def setup(bot):
    await bot.add_cog(AutoMod(bot))
