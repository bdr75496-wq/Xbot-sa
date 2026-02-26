import discord
from discord.ext import commands
from discord import app_commands
import re, time
from collections import defaultdict

BAD_WORDS = ["كلمة1", "كلمة2"]  # أضف الكلمات المحظورة هنا
spam_tracker = defaultdict(list)

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.anti_link = {}
        self.anti_spam = {}
        self.anti_bad = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        gid = str(message.guild.id)

        if self.anti_link.get(gid):
            if not message.author.guild_permissions.manage_messages:
                url_pattern = re.compile(r'https?://\S+|www\.\S+|discord\.gg/\S+')
                if url_pattern.search(message.content):
                    await message.delete()
                    await message.channel.send(f"🚫 {message.author.mention} ممنوع إرسال الروابط!", delete_after=5)
                    return

        if self.anti_bad.get(gid):
            for word in BAD_WORDS:
                if word.lower() in message.content.lower():
                    await message.delete()
                    await message.channel.send(f"🚫 {message.author.mention} رسالتك تحتوي على كلمة محظورة!", delete_after=5)
                    return

        if self.anti_spam.get(gid):
            uid = message.author.id
            now = time.time()
            spam_tracker[uid] = [t for t in spam_tracker[uid] if now - t < 5]
            spam_tracker[uid].append(now)
            if len(spam_tracker[uid]) >= 5:
                await message.delete()
                await message.channel.send(f"🚫 {message.author.mention} لا تقم بالسبام!", delete_after=5)

    @app_commands.command(name="antilink", description="تفعيل/إيقاف فلتر الروابط")
    @app_commands.choices(status=[app_commands.Choice(name="تفعيل", value="on"), app_commands.Choice(name="إيقاف", value="off")])
    @app_commands.checks.has_permissions(manage_guild=True)
    async def antilink(self, interaction: discord.Interaction, status: str):
        self.anti_link[str(interaction.guild.id)] = (status == "on")
        state = "مفعّل ✅" if status == "on" else "موقوف ❌"
        await interaction.response.send_message(f"🔗 فلتر الروابط: **{state}**")

    @app_commands.command(name="antispam", description="تفعيل/إيقاف فلتر السبام")
    @app_commands.choices(status=[app_commands.Choice(name="تفعيل", value="on"), app_commands.Choice(name="إيقاف", value="off")])
    @app_commands.checks.has_permissions(manage_guild=True)
    async def antispam(self, interaction: discord.Interaction, status: str):
        self.anti_spam[str(interaction.guild.id)] = (status == "on")
        state = "مفعّل ✅" if status == "on" else "موقوف ❌"
        await interaction.response.send_message(f"🛡️ فلتر السبام: **{state}**")

    @app_commands.command(name="antibadwords", description="تفعيل/إيقاف فلتر الكلمات السيئة")
    @app_commands.choices(status=[app_commands.Choice(name="تفعيل", value="on"), app_commands.Choice(name="إيقاف", value="off")])
    @app_commands.checks.has_permissions(manage_guild=True)
    async def antibadwords(self, interaction: discord.Interaction, status: str):
        self.anti_bad[str(interaction.guild.id)] = (status == "on")
        state = "مفعّل ✅" if status == "on" else "موقوف ❌"
        await interaction.response.send_message(f"🤬 فلتر الكلمات السيئة: **{state}**")

async def setup(bot):
    await bot.add_cog(AutoMod(bot))
