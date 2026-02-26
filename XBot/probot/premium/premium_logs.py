import discord
from discord.ext import commands
from discord import app_commands
import json, os

def load_logs():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists("data/probot_adv_logs.json"):
        return {}
    with open("data/probot_adv_logs.json", "r") as f:
        return json.load(f)

def save_logs(data):
    with open("data/probot_adv_logs.json", "w") as f:
        json.dump(data, f, indent=4)

class AdvancedLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_log_channel(self, guild):
        data = load_logs()
        cid = data.get(str(guild.id), {}).get("channel")
        return self.bot.get_channel(cid) if cid else None

    @app_commands.command(name="setlogs-advanced", description="إعداد سجلات متقدمة مع معلومات الدعوات")
    @app_commands.checks.has_permissions(administrator=True)
    async def setlogs_advanced(self, interaction: discord.Interaction, channel: discord.TextChannel):
        data = load_logs()
        gid = str(interaction.guild.id)
        data[gid] = {"channel": channel.id}
        save_logs(data)
        embed = discord.Embed(title="📋 سجلات متقدمة", color=discord.Color.blue())
        embed.add_field(name="القناة", value=channel.mention)
        embed.description = "تم تفعيل السجلات المتقدمة!\n• اسم من دعا العضو\n• كود الدعوة\n• عدد الاستخدامات\n• معلومات الحساب المفصلة"
        await interaction.response.send_message(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        ch = await self.get_log_channel(member.guild)
        if not ch:
            return
        inviter = "غير معروف"
        invite_code = "غير معروف"
        invite_uses = "؟"
        try:
            invites = await member.guild.invites()
            for inv in invites:
                if inv.uses and inv.uses > 0:
                    inviter = str(inv.inviter) if inv.inviter else "غير معروف"
                    invite_code = inv.code
                    invite_uses = inv.uses
                    break
        except:
            pass
        embed = discord.Embed(title="📥 عضو جديد انضم", color=discord.Color.green())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="العضو", value=f"{member.mention} ({member})", inline=False)
        embed.add_field(name="الرقم التعريفي", value=str(member.id), inline=True)
        embed.add_field(name="عمر الحساب", value=member.created_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="من دعاه", value=inviter, inline=True)
        embed.add_field(name="كود الدعوة", value=invite_code, inline=True)
        embed.add_field(name="عدد الاستخدامات", value=str(invite_uses), inline=True)
        embed.add_field(name="إجمالي الأعضاء", value=str(member.guild.member_count), inline=True)
        await ch.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        ch = await self.get_log_channel(member.guild)
        if not ch:
            return
        embed = discord.Embed(title="📤 عضو غادر", color=discord.Color.red())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="العضو", value=f"{member} ({member.id})", inline=False)
        embed.add_field(name="الأدوار التي كانت لديه", value=" ".join([r.mention for r in member.roles[1:]]) or "لا يوجد", inline=False)
        if member.joined_at:
            embed.add_field(name="مدة وجوده", value=str((discord.utils.utcnow() - member.joined_at).days) + " يوم", inline=True)
        await ch.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        ch = await self.get_log_channel(message.guild)
        if not ch:
            return
        embed = discord.Embed(title="🗑️ رسالة محذوفة", color=discord.Color.greyple())
        embed.add_field(name="المرسل", value=f"{message.author.mention} ({message.author})", inline=True)
        embed.add_field(name="القناة", value=message.channel.mention, inline=True)
        embed.add_field(name="المحتوى", value=message.content[:1024] or "لا يوجد نص", inline=False)
        if message.attachments:
            embed.add_field(name="المرفقات", value="\n".join([a.filename for a in message.attachments]), inline=False)
        await ch.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content:
            return
        ch = await self.get_log_channel(before.guild)
        if not ch:
            return
        embed = discord.Embed(title="✏️ رسالة معدّلة", color=discord.Color.blue())
        embed.add_field(name="المرسل", value=f"{before.author.mention} ({before.author})", inline=True)
        embed.add_field(name="القناة", value=before.channel.mention, inline=True)
        embed.add_field(name="قبل التعديل", value=before.content[:512] or "فارغ", inline=False)
        embed.add_field(name="بعد التعديل", value=after.content[:512] or "فارغ", inline=False)
        embed.add_field(name="رابط الرسالة", value=f"[اضغط هنا]({after.jump_url})", inline=False)
        await ch.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AdvancedLogs(bot))
