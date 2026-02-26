import discord
from discord import app_commands
from discord.ext import commands
import json, os, re
from collections import defaultdict
import asyncio

spam_tracker = defaultdict(list)

def load_protection():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists("data/protection.json"):
        return {}
    with open("data/protection.json", "r") as f:
        return json.load(f)

def save_protection(data):
    with open("data/protection.json", "w") as f:
        json.dump(data, f, indent=4)

class Protection(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="anti-link", description="تفعيل/تعطيل فلتر الروابط")
    @app_commands.describe(enabled="تفعيل أو تعطيل")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def anti_link(self, interaction: discord.Interaction, enabled: bool):
        data = load_protection()
        gid = str(interaction.guild.id)
        if gid not in data:
            data[gid] = {}
        data[gid]["anti_link"] = enabled
        save_protection(data)
        status = "✅ تم التفعيل" if enabled else "❌ تم التعطيل"
        await interaction.response.send_message(f"{status} لفلتر الروابط")

    @app_commands.command(name="anti-spam", description="تفعيل/تعطيل فلتر السبام")
    @app_commands.describe(enabled="تفعيل أو تعطيل")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def anti_spam(self, interaction: discord.Interaction, enabled: bool):
        data = load_protection()
        gid = str(interaction.guild.id)
        if gid not in data:
            data[gid] = {}
        data[gid]["anti_spam"] = enabled
        save_protection(data)
        status = "✅ تم التفعيل" if enabled else "❌ تم التعطيل"
        await interaction.response.send_message(f"{status} لفلتر السبام")

    @app_commands.command(name="anti-raid", description="تفعيل/تعطيل الحماية من الريد")
    @app_commands.describe(enabled="تفعيل أو تعطيل")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def anti_raid(self, interaction: discord.Interaction, enabled: bool):
        data = load_protection()
        gid = str(interaction.guild.id)
        if gid not in data:
            data[gid] = {}
        data[gid]["anti_raid"] = enabled
        save_protection(data)
        status = "✅ تم التفعيل" if enabled else "❌ تم التعطيل"
        await interaction.response.send_message(f"{status} للحماية من الريد")

    @app_commands.command(name="anti-badwords", description="إضافة كلمات محظورة")
    @app_commands.describe(words="الكلمات المحظورة مفصولة بفاصلة")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def anti_badwords(self, interaction: discord.Interaction, words: str):
        data = load_protection()
        gid = str(interaction.guild.id)
        if gid not in data:
            data[gid] = {}
        data[gid]["bad_words"] = words.split(",")
        save_protection(data)
        await interaction.response.send_message(f"✅ تم إضافة الكلمات المحظورة")

    @app_commands.command(name="whitelist", description="إضافة عضو للقائمة البيضاء")
    @app_commands.describe(member="العضو")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def whitelist(self, interaction: discord.Interaction, member: discord.Member):
        data = load_protection()
        gid = str(interaction.guild.id)
        if gid not in data:
            data[gid] = {}
        if "whitelist" not in data[gid]:
            data[gid]["whitelist"] = []
        if str(member.id) not in data[gid]["whitelist"]:
            data[gid]["whitelist"].append(str(member.id))
        save_protection(data)
        await interaction.response.send_message(f"✅ تم إضافة {member.mention} للقائمة البيضاء")

    @app_commands.command(name="blacklist", description="إضافة عضو للقائمة السوداء")
    @app_commands.describe(member="العضو")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def blacklist(self, interaction: discord.Interaction, member: discord.Member):
        data = load_protection()
        gid = str(interaction.guild.id)
        if gid not in data:
            data[gid] = {}
        if "blacklist" not in data[gid]:
            data[gid]["blacklist"] = []
        if str(member.id) not in data[gid]["blacklist"]:
            data[gid]["blacklist"].append(str(member.id))
        save_protection(data)
        await interaction.response.send_message(f"✅ تم إضافة {member.mention} للقائمة السوداء")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        data = load_protection()
        gid = str(message.guild.id)
        if gid not in data:
            return

        uid = str(message.author.id)
        whitelist = data[gid].get("whitelist", [])
        if uid in whitelist:
            return

        # فلتر الروابط
        if data[gid].get("anti_link"):
            url_pattern = re.compile(r'https?://\S+|discord\.gg/\S+')
            if url_pattern.search(message.content):
                await message.delete()
                await message.channel.send(f"❌ {message.author.mention} لا يسمح بالروابط!", delete_after=3)
                return

        # فلتر الكلمات
        bad_words = data[gid].get("bad_words", [])
        for word in bad_words:
            if word.strip().lower() in message.content.lower():
                await message.delete()
                await message.channel.send(f"❌ {message.author.mention} رسالتك تحتوي على كلمة محظورة!", delete_after=3)
                return

        # فلتر السبام
        if data[gid].get("anti_spam"):
            import time
            now = time.time()
            spam_tracker[uid] = [t for t in spam_tracker[uid] if now - t < 5]
            spam_tracker[uid].append(now)
            if len(spam_tracker[uid]) >= 5:
                await message.delete()
                await message.channel.send(f"❌ {message.author.mention} لا تقم بالسبام!", delete_after=3)

async def setup(bot):
    await bot.add_cog(Protection(bot))
