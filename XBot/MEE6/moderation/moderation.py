import discord
from discord.ext import commands
from discord import app_commands

warnings_db = {}

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="clear", description="حذف عدد من الرسائل")
    @app_commands.describe(amount="عدد الرسائل")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int):
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"🗑️ تم حذف **{len(deleted)}** رسالة بنجاح.", ephemeral=True)

    @app_commands.command(name="slowmode", description="تفعيل وضع البطيء")
    @app_commands.describe(seconds="الثواني (0 لإيقافه)")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def slowmode(self, interaction: discord.Interaction, seconds: int):
        await interaction.channel.edit(slowmode_delay=seconds)
        if seconds == 0:
            await interaction.response.send_message("✅ تم إيقاف وضع البطيء.")
        else:
            await interaction.response.send_message(f"⏱️ تم تفعيل وضع البطيء: **{seconds}** ثانية.")

    @app_commands.command(name="warn", description="إعطاء تحذير لعضو")
    @app_commands.describe(member="العضو", reason="السبب")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str = "بدون سبب"):
        gid = str(interaction.guild.id)
        uid = str(member.id)
        if gid not in warnings_db:
            warnings_db[gid] = {}
        if uid not in warnings_db[gid]:
            warnings_db[gid][uid] = []
        warnings_db[gid][uid].append(reason)
        count = len(warnings_db[gid][uid])
        embed = discord.Embed(title="⚠️ تم التحذير", color=discord.Color.yellow())
        embed.add_field(name="العضو", value=member.mention)
        embed.add_field(name="السبب", value=reason)
        embed.add_field(name="عدد التحذيرات", value=str(count))
        embed.add_field(name="المشرف", value=interaction.user.mention)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="unwarn", description="إزالة آخر تحذير لعضو")
    @app_commands.describe(member="العضو")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def unwarn(self, interaction: discord.Interaction, member: discord.Member):
        gid = str(interaction.guild.id)
        uid = str(member.id)
        if gid in warnings_db and uid in warnings_db[gid] and warnings_db[gid][uid]:
            warnings_db[gid][uid].pop()
            await interaction.response.send_message(f"✅ تم إزالة آخر تحذير عن {member.mention}.")
        else:
            await interaction.response.send_message("❌ لا يوجد تحذيرات لهذا العضو!", ephemeral=True)

    @app_commands.command(name="infractions", description="عرض تحذيرات عضو")
    @app_commands.describe(member="العضو")
    async def infractions(self, interaction: discord.Interaction, member: discord.Member):
        gid = str(interaction.guild.id)
        uid = str(member.id)
        warns = warnings_db.get(gid, {}).get(uid, [])
        if not warns:
            await interaction.response.send_message(f"✅ {member.mention} ليس لديه أي تحذيرات.")
            return
        embed = discord.Embed(title=f"📋 تحذيرات {member.display_name}", color=discord.Color.orange())
        for i, r in enumerate(warns, 1):
            embed.add_field(name=f"تحذير {i}", value=r, inline=False)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
