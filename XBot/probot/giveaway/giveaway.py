import discord
from discord import app_commands
from discord.ext import commands
import asyncio, random, json, os
from datetime import datetime, timedelta

def load_giveaways():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists("data/giveaways.json"):
        return {}
    with open("data/giveaways.json", "r") as f:
        return json.load(f)

def save_giveaways(data):
    with open("data/giveaways.json", "w") as f:
        json.dump(data, f, indent=4)

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="giveaway-create", description="إنشاء قيف أواي")
    @app_commands.describe(prize="الجائزة", duration="المدة بالدقائق", winners="عدد الفائزين")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def giveaway_create(self, interaction: discord.Interaction, prize: str, duration: int = 60, winners: int = 1):
        end_time = datetime.utcnow() + timedelta(minutes=duration)
        
        embed = discord.Embed(title="🎉 قيف أواي!", color=discord.Color.gold())
        embed.add_field(name="الجائزة", value=prize)
        embed.add_field(name="عدد الفائزين", value=winners)
        embed.add_field(name="ينتهي", value=f"<t:{int(end_time.timestamp())}:R>")
        embed.set_footer(text="اضغط 🎉 للمشاركة!")
        
        await interaction.response.send_message(embed=embed)
        msg = await interaction.original_response()
        await msg.add_reaction("🎉")
        
        data = load_giveaways()
        data[str(msg.id)] = {
            "prize": prize,
            "winners": winners,
            "end_time": end_time.isoformat(),
            "channel_id": interaction.channel_id,
            "message_id": msg.id
        }
        save_giveaways(data)
        
        await asyncio.sleep(duration * 60)
        await self._end_giveaway(msg.id, interaction.channel)

    async def _end_giveaway(self, message_id, channel):
        try:
            msg = await channel.fetch_message(message_id)
            reaction = discord.utils.get(msg.reactions, emoji="🎉")
            if reaction:
                users = [u async for u in reaction.users() if not u.bot]
                data = load_giveaways()
                gw = data.get(str(message_id))
                if users and gw:
                    winners = random.sample(users, min(gw["winners"], len(users)))
                    winners_mention = " ".join([w.mention for w in winners])
                    await channel.send(f"🎉 تهانينا {winners_mention}! فزتم بـ **{gw['prize']}**!")
                else:
                    await channel.send("❌ لا يوجد مشاركون في القيف أواي!")
        except:
            pass

    @app_commands.command(name="giveaway-end", description="إنهاء قيف أواي")
    @app_commands.describe(message_id="ID الرسالة")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def giveaway_end(self, interaction: discord.Interaction, message_id: str):
        await interaction.response.send_message("✅ جاري إنهاء القيف أواي...")
        await self._end_giveaway(int(message_id), interaction.channel)

    @app_commands.command(name="giveaway-reroll", description="إعادة سحب الفائز")
    @app_commands.describe(message_id="ID الرسالة")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def giveaway_reroll(self, interaction: discord.Interaction, message_id: str):
        await interaction.response.send_message("🔄 جاري إعادة السحب...")
        await self._end_giveaway(int(message_id), interaction.channel)

async def setup(bot):
    await bot.add_cog(Giveaway(bot))
