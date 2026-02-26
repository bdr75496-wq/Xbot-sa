import discord
from discord.ext import commands
from discord import app_commands
import asyncio, random
from datetime import datetime, timedelta

giveaways = {}

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="gstart", description="بدء قيف أواي")
    @app_commands.describe(prize="الجائزة", duration="المدة بالدقائق", winners="عدد الفائزين")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def gstart(self, interaction: discord.Interaction, prize: str, duration: int = 60, winners: int = 1):
        end_time = datetime.utcnow() + timedelta(minutes=duration)
        embed = discord.Embed(title="🎉 قيف أواي!", color=discord.Color.gold())
        embed.add_field(name="الجائزة", value=prize)
        embed.add_field(name="عدد الفائزين", value=str(winners))
        embed.add_field(name="ينتهي", value=f"<t:{int(end_time.timestamp())}:R>")
        embed.set_footer(text="اضغط 🎉 للمشاركة!")
        await interaction.response.send_message(embed=embed)
        msg = await interaction.original_response()
        await msg.add_reaction("🎉")
        giveaways[str(msg.id)] = {"prize": prize, "winners": winners, "channel_id": interaction.channel_id}
        await asyncio.sleep(duration * 60)
        await self._end_giveaway(msg.id, interaction.channel)

    async def _end_giveaway(self, message_id, channel):
        try:
            msg = await channel.fetch_message(message_id)
            reaction = discord.utils.get(msg.reactions, emoji="🎉")
            if reaction:
                users = [u async for u in reaction.users() if not u.bot]
                gw = giveaways.get(str(message_id))
                if users and gw:
                    winners = random.sample(users, min(gw["winners"], len(users)))
                    winners_mention = " ".join([w.mention for w in winners])
                    embed = discord.Embed(title="🎉 انتهى القيف أواي!", color=discord.Color.gold())
                    embed.add_field(name="الجائزة", value=gw["prize"])
                    embed.add_field(name="الفائزون", value=winners_mention)
                    await channel.send(embed=embed)
                    await channel.send(f"🎊 تهانينا {winners_mention}! فزتم بـ **{gw['prize']}**!")
                else:
                    await channel.send("❌ لا يوجد مشاركون في القيف أواي!")
        except:
            pass

    @app_commands.command(name="gend", description="إنهاء قيف أواي")
    @app_commands.describe(message_id="الرقم التعريفي للرسالة")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def gend(self, interaction: discord.Interaction, message_id: str):
        await interaction.response.send_message("✅ جاري إنهاء القيف أواي...")
        await self._end_giveaway(int(message_id), interaction.channel)

    @app_commands.command(name="greroll", description="إعادة اختيار فائز")
    @app_commands.describe(message_id="الرقم التعريفي للرسالة")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def greroll(self, interaction: discord.Interaction, message_id: str):
        await interaction.response.send_message("🔄 جاري إعادة السحب...")
        await self._end_giveaway(int(message_id), interaction.channel)

async def setup(bot):
    await bot.add_cog(Giveaway(bot))
