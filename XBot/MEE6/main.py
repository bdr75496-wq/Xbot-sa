import discord
from discord.ext import commands
import asyncio

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ بوت MEE6 شغّال: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ تم مزامنة {len(synced)} أمر بنجاح")
    except Exception as e:
        print(f"❌ خطأ في المزامنة: {e}")

async def main():
    async with bot:
        await bot.load_extension("MEE6.moderation.ban")
        await bot.load_extension("MEE6.moderation.tempban")
        await bot.load_extension("MEE6.moderation.unban")
        await bot.load_extension("MEE6.moderation.kick")
        await bot.load_extension("MEE6.moderation.mute")
        await bot.load_extension("MEE6.moderation.moderation")
        await bot.load_extension("MEE6.levels.levels")
        await bot.load_extension("MEE6.welcome.welcome")
        await bot.load_extension("MEE6.info.info")
        await bot.load_extension("MEE6.automod.automod")
        await bot.load_extension("MEE6.logs.logs")
        await bot.load_extension("MEE6.reaction_roles.reaction_roles")
        await bot.load_extension("MEE6.custom_commands.custom_commands")
        await bot.load_extension("MEE6.auto_messages.auto_messages")
        await bot.start("TOKEN_HERE")  # ضع التوكن هنا

asyncio.run(main())
