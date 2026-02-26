import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta
import json, os

def load_warnings():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists("data/carlbot_warnings.json"):
        return {}
    with open("data/carlbot_warnings.json", "r") as f:
        return json.load(f)

def save_warnings(data):
    with open("data/carlbot_warnings.json", "w") as f:
        json.dump(data, f, indent=4)

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ban", description="حظر عضو من السيرفر")
    @app_commands.describe(member="العضو", reason="السبب")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "بدون سبب"):
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("❌ لا تستطيع حظر شخص رتبته أعلى منك!", ephemeral=True)
        await member.ban(reason=reason)
        embed = discord.Embed(title="🔨 تم الحظر", color=discord.Color.red())
        embed.add_field(name="العضو", value=member.mention)
        embed.add_field(name="السبب", value=reason)
        embed.add_field(name="المشرف", value=interaction.user.mention)
        embed.set_footer(text=f"الرقم التعريفي: {member.id}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="tempban", description="حظر مؤقت لعضو")
    @app_commands.describe(member="العضو", duration="المدة بالدقائق", reason="السبب")
    @app_commands.checks.has_permissions(ban_members=True)
    async def tempban(self, interaction: discord.Interaction, member: discord.Member, duration: int, reason: str = "بدون سبب"):
        await member.ban(reason=reason)
        embed = discord.Embed(title="⏳ حظر مؤقت", color=discord.Color.orange())
        embed.add_field(name="العضو", value=member.mention)
        embed.add_field(name="المدة", value=f"{duration} دقيقة")
        embed.add_field(name="السبب", value=reason)
        embed.add_field(name="المشرف", value=interaction.user.mention)
        await interaction.response.send_message(embed=embed)
        import asyncio
        await asyncio.sleep(duration * 60)
        await interaction.guild.unban(member)

    @app_commands.command(name="unban", description="فك حظر عضو")
    @app_commands.describe(user_id="الرقم التعريفي للعضو", reason="السبب")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user_id: str, reason: str = "بدون سبب"):
        try:
            user = await self.bot.fetch_user(int(user_id))
            await interaction.guild.unban(user, reason=reason)
            embed = discord.Embed(title="✅ تم فك الحظر", color=discord.Color.green())
            embed.add_field(name="العضو", value=str(user))
            embed.add_field(name="السبب", value=reason)
            embed.add_field(name="المشرف", value=interaction.user.mention)
            await interaction.response.send_message(embed=embed)
        except:
            await interaction.response.send_message("❌ لم يتم العثور على العضو!", ephemeral=True)

    @app_commands.command(name="kick", description="طرد عضو من السيرفر")
    @app_commands.describe(member="العضو", reason="السبب")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "بدون سبب"):
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("❌ لا تستطيع طرد شخص رتبته أعلى منك!", ephemeral=True)
        await member.kick(reason=reason)
        embed = discord.Embed(title="👢 تم الطرد", color=discord.Color.orange())
        embed.add_field(name="العضو", value=member.mention)
        embed.add_field(name="السبب", value=reason)
        embed.add_field(name="المشرف", value=interaction.user.mention)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="mute", description="كتم عضو")
    @app_commands.describe(member="العضو", duration="المدة بالدقائق", reason="السبب")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute(self, interaction: discord.Interaction, member: discord.Member, duration: int = 10, reason: str = "بدون سبب"):
        await member.timeout(timedelta(minutes=duration), reason=reason)
        embed = discord.Embed(title="🔇 تم الكتم", color=discord.Color.greyple())
        embed.add_field(name="العضو", value=member.mention)
        embed.add_field(name="المدة", value=f"{duration} دقيقة")
        embed.add_field(name="السبب", value=reason)
        embed.add_field(name="المشرف", value=interaction.user.mention)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="unmute", description="إزالة الكتم عن عضو")
    @app_commands.describe(member="العضو")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        await member.timeout(None)
        embed = discord.Embed(title="🔊 تم إزالة الكتم", color=discord.Color.green())
        embed.add_field(name="العضو", value=member.mention)
        embed.add_field(name="المشرف", value=interaction.user.mention)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="warn", description="تحذير عضو")
    @app_commands.describe(member="العضو", reason="السبب")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str = "بدون سبب"):
        data = load_warnings()
        uid = str(member.id)
        if uid not in data:
            data[uid] = []
        data[uid].append({"reason": reason, "by": str(interaction.user.id)})
        save_warnings(data)
        embed = discord.Embed(title="⚠️ تم التحذير", color=discord.Color.yellow())
        embed.add_field(name="العضو", value=member.mention)
        embed.add_field(name="السبب", value=reason)
        embed.add_field(name="عدد التحذيرات", value=str(len(data[uid])))
        embed.add_field(name="المشرف", value=interaction.user.mention)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="warnings", description="عرض تحذيرات عضو")
    @app_commands.describe(member="العضو")
    async def warnings(self, interaction: discord.Interaction, member: discord.Member):
        data = load_warnings()
        warns = data.get(str(member.id), [])
        embed = discord.Embed(title=f"⚠️ تحذيرات {member.display_name}", color=discord.Color.yellow())
        if not warns:
            embed.description = "✅ لا توجد تحذيرات"
        else:
            for i, w in enumerate(warns, 1):
                embed.add_field(name=f"تحذير {i}", value=w["reason"], inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="purge", description="حذف عدد من الرسائل")
    @app_commands.describe(amount="عدد الرسائل")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction, amount: int):
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

    @app_commands.command(name="lock", description="قفل الروم")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def lock(self, interaction: discord.Interaction):
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
        await interaction.response.send_message("🔒 تم قفل الروم.")

    @app_commands.command(name="unlock", description="فتح الروم")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def unlock(self, interaction: discord.Interaction):
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
        await interaction.response.send_message("🔓 تم فتح الروم.")

    @app_commands.command(name="nick", description="تغيير لقب عضو")
    @app_commands.describe(member="العضو", nickname="اللقب الجديد")
    @app_commands.checks.has_permissions(manage_nicknames=True)
    async def nick(self, interaction: discord.Interaction, member: discord.Member, nickname: str):
        await member.edit(nick=nickname)
        embed = discord.Embed(title="✏️ تم تغيير اللقب", color=discord.Color.blue())
        embed.add_field(name="العضو", value=member.mention)
        embed.add_field(name="اللقب الجديد", value=nickname)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="role", description="إعطاء/إزالة رتبة من عضو")
    @app_commands.describe(member="العضو", role="الرتبة")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def role(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        if role in member.roles:
            await member.remove_roles(role)
            embed = discord.Embed(title="➖ تم إزالة الرتبة", color=discord.Color.red())
        else:
            await member.add_roles(role)
            embed = discord.Embed(title="➕ تم إضافة الرتبة", color=discord.Color.green())
        embed.add_field(name="العضو", value=member.mention)
        embed.add_field(name="الرتبة", value=role.mention)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
