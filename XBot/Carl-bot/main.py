import discord
from discord.ext import commands
import asyncio

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ بوت Carl-bot شغّال: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ تم مزامنة {len(synced)} أمر بنجاح")
    except Exception as e:
        print(f"❌ خطأ في المزامنة: {e}")

async def main():
    async with bot:
        await bot.load_extension("Carl-bot.moderation.moderation")
        await bot.load_extension("Carl-bot.automod.automod")
        await bot.load_extension("Carl-bot.reaction_roles.reaction_roles")
        await bot.load_extension("Carl-bot.info.info")
        await bot.load_extension("Carl-bot.logs.logs")
        await bot.load_extension("Carl-bot.giveaway.giveaway")
        await bot.load_extension("Carl-bot.tags.tags")
        await bot.load_extension("Carl-bot.starboard.starboard")
        await bot.start("TOKEN_HERE")  # ضع التوكن هنا

asyncio.run(main())
