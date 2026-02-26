import discord
from discord.ext import commands
from discord import app_commands
import json, os

def load_logs():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists("data/mee6_logs.json"):
        return {}
    with open("data/mee6_logs.json", "r") as f:
        return json.load(f)

def save_logs(data):
    with open("data/mee6_logs.json", "w") as f:
        json.dump(data, f, indent=4)

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_log_channel(self, guild):
        data = load_logs()
        cid = data.get(str(guild.id))
        return self.bot.get_channel(cid) if cid else None

    @app_commands.command(name="setlogs", description="تحديد روم السجلات")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setlogs(self, interaction: discord.Interaction, channel: discord.TextChannel):
        data = load_logs()
        data[str(interaction.guild.id)] = channel.id
        save_logs(data)
        await interaction.response.send_message(f"✅ تم تعيين روم السجلات على {channel.mention}")

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        ch = await self.get_log_channel(guild)
        if ch:
            embed = discord.Embed(title="🔨 تم حظر عضو", color=discord.Color.red())
            embed.add_field(name="العضو", value=str(user))
            embed.add_field(name="الرقم التعريفي", value=str(user.id))
            await ch.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        ch = await self.get_log_channel(guild)
        if ch:
            embed = discord.Embed(title="✅ تم فك الحظر", color=discord.Color.green())
            embed.add_field(name="العضو", value=str(user))
            await ch.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        ch = await self.get_log_channel(member.guild)
        if ch:
            embed = discord.Embed(title="👢 غادر عضو", color=discord.Color.orange())
            embed.add_field(name="العضو", value=str(member))
            await ch.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        ch = await self.get_log_channel(member.guild)
        if ch:
            embed = discord.Embed(title="👋 انضم عضو جديد", color=discord.Color.green())
            embed.add_field(name="العضو", value=member.mention)
            await ch.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        ch = await self.get_log_channel(message.guild)
        if ch:
            embed = discord.Embed(title="🗑️ رسالة محذوفة", color=discord.Color.greyple())
            embed.add_field(name="العضو", value=str(message.author), inline=True)
            embed.add_field(name="الروم", value=message.channel.mention, inline=True)
            embed.add_field(name="المحتوى", value=message.content or "لا يوجد نص", inline=False)
            await ch.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content:
            return
        ch = await self.get_log_channel(before.guild)
        if ch:
            embed = discord.Embed(title="✏️ رسالة معدّلة", color=discord.Color.blue())
            embed.add_field(name="العضو", value=str(before.author), inline=True)
            embed.add_field(name="الروم", value=before.channel.mention, inline=True)
            embed.add_field(name="قبل", value=before.content or "فارغ", inline=False)
            embed.add_field(name="بعد", value=after.content or "فارغ", inline=False)
            await ch.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Logs(bot))
