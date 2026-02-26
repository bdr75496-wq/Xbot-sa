import discord
from discord.ext import commands
from discord import app_commands
import json, os

def load_rr():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists("data/carlbot_adv_rr.json"):
        return {}
    with open("data/carlbot_adv_rr.json", "r") as f:
        return json.load(f)

def save_rr(data):
    with open("data/carlbot_adv_rr.json", "w") as f:
        json.dump(data, f, indent=4)

class AdvancedReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="rr-create-advanced", description="إنشاء رتب تفاعلية بأزرار")
    @app_commands.describe(title="عنوان الرسالة", description="الوصف")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def rr_create_advanced(self, interaction: discord.Interaction, title: str, description: str):
        embed = discord.Embed(title=f"🎭 {title}", description=description, color=discord.Color.blue())
        embed.set_footer(text="اضغط على الزر للحصول على الرتبة")
        msg = await interaction.channel.send(embed=embed)
        data = load_rr()
        gid = str(interaction.guild.id)
        if gid not in data: data[gid] = {}
        data[gid][str(msg.id)] = {"roles": [], "type": "button"}
        save_rr(data)
        await interaction.response.send_message(f"✅ تم إنشاء رسالة الرتب!\nالرقم: `{msg.id}`\nاستخدم `/rr-add-button` لإضافة أزرار.", ephemeral=True)

    @app_commands.command(name="rr-add-button", description="إضافة زر رتبة للرسالة")
    @app_commands.describe(message_id="رقم الرسالة", role="الرتبة", label="نص الزر", emoji="إيموجي (اختياري)")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def rr_add_button(self, interaction: discord.Interaction, message_id: str, role: discord.Role, label: str, emoji: str = None):
        data = load_rr()
        gid = str(interaction.guild.id)
        if gid not in data or message_id not in data[gid]:
            return await interaction.response.send_message("❌ الرسالة غير موجودة!", ephemeral=True)
        if len(data[gid][message_id]["roles"]) >= 25:
            return await interaction.response.send_message("❌ الحد الأقصى 25 رتبة!", ephemeral=True)
        data[gid][message_id]["roles"].append({"role_id": role.id, "label": label, "emoji": emoji})
        save_rr(data)
        embed = discord.Embed(title="✅ تم إضافة الزر", color=discord.Color.blue())
        embed.add_field(name="الرتبة", value=role.mention)
        embed.add_field(name="النص", value=label)
        if emoji: embed.add_field(name="الإيموجي", value=emoji)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="rr-limit", description="تحديد عدد الرتب المسموح باختيارها")
    @app_commands.describe(message_id="رقم الرسالة", max_roles="الحد الأقصى")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def rr_limit(self, interaction: discord.Interaction, message_id: str, max_roles: int):
        data = load_rr()
        gid = str(interaction.guild.id)
        if gid in data and message_id in data[gid]:
            data[gid][message_id]["max_roles"] = max_roles
            save_rr(data)
            embed = discord.Embed(title="🔢 تم تحديد الحد", color=discord.Color.blue())
            embed.add_field(name="الحد الأقصى", value=f"{max_roles} رتبة")
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ الرسالة غير موجودة!", ephemeral=True)

    @app_commands.command(name="autorole-multi", description="إعطاء رتب متعددة تلقائياً عند الانضمام")
    @app_commands.describe(role1="الرتبة الأولى", role2="الرتبة الثانية (اختياري)", role3="الرتبة الثالثة (اختياري)")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def autorole_multi(self, interaction: discord.Interaction, role1: discord.Role, role2: discord.Role = None, role3: discord.Role = None):
        data = load_rr()
        gid = str(interaction.guild.id)
        if gid not in data: data[gid] = {}
        roles = [role1.id]
        if role2: roles.append(role2.id)
        if role3: roles.append(role3.id)
        data[gid]["autoroles"] = roles
        save_rr(data)
        role_names = [role1.mention] + ([role2.mention] if role2 else []) + ([role3.mention] if role3 else [])
        embed = discord.Embed(title="🎭 رتب تلقائية متعددة", color=discord.Color.blue())
        embed.add_field(name="الرتب", value=" | ".join(role_names))
        embed.description = "كل عضو جديد سيحصل على هذه الرتب تلقائياً!"
        await interaction.response.send_message(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        data = load_rr()
        gid = str(member.guild.id)
        for role_id in data.get(gid, {}).get("autoroles", []):
            role = member.guild.get_role(role_id)
            if role:
                try: await member.add_roles(role)
                except: pass

async def setup(bot):
    await bot.add_cog(AdvancedReactionRoles(bot))
