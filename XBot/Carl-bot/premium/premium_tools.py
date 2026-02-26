import discord
from discord.ext import commands
from discord import app_commands
import json, os, asyncio

def load_triggers():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists("data/carlbot_triggers.json"):
        return {}
    with open("data/carlbot_triggers.json", "r") as f:
        return json.load(f)

def save_triggers(data):
    with open("data/carlbot_triggers.json", "w") as f:
        json.dump(data, f, indent=4)

class AdvancedTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="remind-server", description="إنشاء تذكير لكل السيرفر")
    @app_commands.describe(channel="قناة التذكير", message="رسالة التذكير", minutes="بعد كم دقيقة")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def remind_server(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str, minutes: int):
        embed = discord.Embed(title="⏰ تم إنشاء التذكير", color=discord.Color.blue())
        embed.add_field(name="القناة", value=channel.mention)
        embed.add_field(name="بعد", value=f"{minutes} دقيقة")
        embed.add_field(name="الرسالة", value=message)
        await interaction.response.send_message(embed=embed)
        await asyncio.sleep(minutes * 60)
        remind_embed = discord.Embed(title="🔔 تذكير!", description=message, color=discord.Color.gold())
        await channel.send(embed=remind_embed)

    @app_commands.command(name="remind-me", description="تذكير شخصي يصلك في الـ DM")
    @app_commands.describe(message="رسالة التذكير", minutes="بعد كم دقيقة")
    async def remind_me(self, interaction: discord.Interaction, message: str, minutes: int):
        embed = discord.Embed(title="⏰ تم إنشاء تذكيرك", color=discord.Color.blue())
        embed.add_field(name="بعد", value=f"{minutes} دقيقة")
        embed.add_field(name="الرسالة", value=message)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await asyncio.sleep(minutes * 60)
        try:
            dm_embed = discord.Embed(title="🔔 تذكيرك!", description=message, color=discord.Color.gold())
            await interaction.user.send(embed=dm_embed)
        except:
            await interaction.channel.send(f"{interaction.user.mention} 🔔 تذكيرك: {message}")

    @app_commands.command(name="trigger-add", description="إضافة رد تلقائي على كلمة أو جملة")
    @app_commands.describe(trigger="الكلمة المشغِّلة", response="الرد التلقائي", exact="مطابقة كاملة للرسالة؟")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def trigger_add(self, interaction: discord.Interaction, trigger: str, response: str, exact: bool = False):
        data = load_triggers()
        gid = str(interaction.guild.id)
        if gid not in data: data[gid] = []
        if len(data[gid]) >= 100:
            return await interaction.response.send_message("❌ الحد الأقصى 100 تريقر!", ephemeral=True)
        data[gid].append({"trigger": trigger.lower(), "response": response, "exact": exact})
        save_triggers(data)
        embed = discord.Embed(title="✅ تم إضافة التريقر", color=discord.Color.blue())
        embed.add_field(name="المشغِّل", value=f"`{trigger}`")
        embed.add_field(name="الرد", value=response[:100])
        embed.add_field(name="النوع", value="مطابقة كاملة" if exact else "يحتوي على الكلمة")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="trigger-remove", description="حذف تريقر")
    @app_commands.describe(trigger="الكلمة المشغِّلة")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def trigger_remove(self, interaction: discord.Interaction, trigger: str):
        data = load_triggers()
        gid = str(interaction.guild.id)
        if gid in data:
            data[gid] = [t for t in data[gid] if t["trigger"] != trigger.lower()]
            save_triggers(data)
            await interaction.response.send_message(f"✅ تم حذف التريقر: `{trigger}`")
        else:
            await interaction.response.send_message("❌ لا توجد تريقرز!", ephemeral=True)

    @app_commands.command(name="trigger-list", description="عرض جميع التريقرز")
    async def trigger_list(self, interaction: discord.Interaction):
        data = load_triggers()
        triggers = data.get(str(interaction.guild.id), [])
        if not triggers:
            return await interaction.response.send_message("❌ لا توجد تريقرز بعد.")
        embed = discord.Embed(title="⚡ قائمة التريقرز", color=discord.Color.blue())
        for t in triggers[:15]:
            embed.add_field(name=f"`{t['trigger']}`", value=t["response"][:50], inline=True)
        if len(triggers) > 15:
            embed.set_footer(text=f"إجمالي: {len(triggers)} تريقر")
        await interaction.response.send_message(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        data = load_triggers()
        triggers = data.get(str(message.guild.id), [])
        content = message.content.lower().strip()
        for t in triggers:
            hit = (t["exact"] and content == t["trigger"]) or (not t["exact"] and t["trigger"] in content)
            if hit:
                resp = t["response"].replace("{user}", message.author.mention).replace("{server}", message.guild.name)
                await message.channel.send(resp)
                break

async def setup(bot):
    await bot.add_cog(AdvancedTools(bot))
