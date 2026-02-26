import discord
from discord.ext import commands
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

async def load_cogs():
    # ProBot
    for folder in ["moderation", "levels", "info", "giveaway", "other"]:
        for file in os.listdir(f"probot/{folder}"):
            if file.endswith(".py"):
                await bot.load_extension(f"probot.{folder}.{file[:-3]}")
                print(f"✅ ProBot: {file}")

    # عراق بوت
    for folder in ["tickets", "apply", "welcome", "moderation", "info", "protection", "admin"]:
        for file in os.listdir(f"عراق-بوت/{folder}"):
            if file.endswith(".py"):
                await bot.load_extension(f"عراق-بوت.{folder}.{file[:-3]}")
                print(f"✅ عراق-بوت: {file}")

@bot.event
async def on_ready():
    await load_cogs()
    await bot.tree.sync()
    print(f"\n✅ XBot شغال: {bot.user}")
    print(f"📊 السيرفرات: {len(bot.guilds)}")
    print("🇵🇸 من النهر إلى البحر")

bot.run("TOKEN_هنا")
