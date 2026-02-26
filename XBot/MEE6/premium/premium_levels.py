import discord
from discord.ext import commands
from discord import app_commands
import json, os, random

def load_levels():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists("data/mee6_levels.json"):
        return {}
    with open("data/mee6_levels.json", "r") as f:
        return json.load(f)

def save_levels(data):
    with open("data/mee6_levels.json", "w") as f:
        json.dump(data, f, indent=4)

def load_rewards():
    if not os.path.exists("data/mee6_rewards.json"):
        return {}
    with open("data/mee6_rewards.json", "r") as f:
        return json.load(f)

def save_rewards(data):
    with open("data/mee6_rewards.json", "w") as f:
        json.dump(data, f, indent=4)

class AdvancedLevels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setxp", description="تحديد XP لعضو بشكل مباشر")
    @app_commands.describe(member="العضو", xp="مقدار الـ XP")
    @app_commands.checks.has_permissions(administrator=True)
    async def setxp(self, interaction: discord.Interaction, member: discord.Member, xp: int):
        data = load_levels()
        gid, uid = str(interaction.guild.id), str(member.id)
        if gid not in data: data[gid] = {}
        if uid not in data[gid]: data[gid][uid] = {"xp": 0, "level": 0}
        data[gid][uid]["xp"] = xp
        save_levels(data)
        embed = discord.Embed(title="✅ تم تعديل XP", color=discord.Color.blue())
        embed.add_field(name="العضو", value=member.mention)
        embed.add_field(name="الـ XP الجديد", value=str(xp))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="addxp", description="إضافة XP لعضو")
    @app_commands.describe(member="العضو", xp="مقدار الـ XP للإضافة")
    @app_commands.checks.has_permissions(administrator=True)
    async def addxp(self, interaction: discord.Interaction, member: discord.Member, xp: int):
        data = load_levels()
        gid, uid = str(interaction.guild.id), str(member.id)
        if gid not in data: data[gid] = {}
        if uid not in data[gid]: data[gid][uid] = {"xp": 0, "level": 0}
        data[gid][uid]["xp"] += xp
        save_levels(data)
        embed = discord.Embed(title="➕ تمت إضافة XP", color=discord.Color.blue())
        embed.add_field(name="العضو", value=member.mention)
        embed.add_field(name="XP المضاف", value=str(xp))
        embed.add_field(name="الإجمالي", value=str(data[gid][uid]["xp"]))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="removexp", description="سحب XP من عضو")
    @app_commands.describe(member="العضو", xp="مقدار الـ XP للسحب")
    @app_commands.checks.has_permissions(administrator=True)
    async def removexp(self, interaction: discord.Interaction, member: discord.Member, xp: int):
        data = load_levels()
        gid, uid = str(interaction.guild.id), str(member.id)
        if gid not in data: data[gid] = {}
        if uid not in data[gid]: data[gid][uid] = {"xp": 0, "level": 0}
        data[gid][uid]["xp"] = max(0, data[gid][uid]["xp"] - xp)
        save_levels(data)
        embed = discord.Embed(title="➖ تم سحب XP", color=discord.Color.blue())
        embed.add_field(name="العضو", value=member.mention)
        embed.add_field(name="XP المسحوب", value=str(xp))
        embed.add_field(name="الإجمالي", value=str(data[gid][uid]["xp"]))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="set-xp-rate", description="تعديل سرعة اكتساب XP")
    @app_commands.describe(multiplier="المضاعف مثل 1.5 أو 2.0")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_xp_rate(self, interaction: discord.Interaction, multiplier: float):
        if multiplier < 0.1 or multiplier > 5.0:
            return await interaction.response.send_message("❌ المضاعف يجب أن يكون بين 0.1 و 5.0!", ephemeral=True)
        data = load_levels()
        gid = str(interaction.guild.id)
        if gid not in data: data[gid] = {}
        data[gid]["xp_multiplier"] = multiplier
        save_levels(data)
        embed = discord.Embed(title="⚡ تم تعديل سرعة XP", color=discord.Color.blue())
        embed.add_field(name="المضاعف الجديد", value=f"x{multiplier}")
        embed.description = f"الأعضاء يكسبون XP بمعدل **{multiplier}x** من المعدل الطبيعي!"
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="role-reward", description="إضافة رتبة تلقائية عند الوصول لمستوى")
    @app_commands.describe(level="المستوى المطلوب", role="الرتبة التي تُعطى")
    @app_commands.checks.has_permissions(administrator=True)
    async def role_reward(self, interaction: discord.Interaction, level: int, role: discord.Role):
        data = load_rewards()
        gid = str(interaction.guild.id)
        if gid not in data: data[gid] = {}
        data[gid][str(level)] = role.id
        save_rewards(data)
        embed = discord.Embed(title="🎁 تم إضافة مكافأة المستوى", color=discord.Color.blue())
        embed.add_field(name="المستوى", value=str(level))
        embed.add_field(name="الرتبة", value=role.mention)
        embed.description = f"عند وصول عضو للمستوى **{level}** سيحصل تلقائياً على {role.mention}"
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="role-rewards-list", description="عرض جميع مكافآت المستويات")
    async def role_rewards_list(self, interaction: discord.Interaction):
        data = load_rewards()
        rewards = data.get(str(interaction.guild.id), {})
        if not rewards:
            return await interaction.response.send_message("❌ لا توجد مكافآت مستويات بعد.")
        embed = discord.Embed(title="🎁 مكافآت المستويات", color=discord.Color.blue())
        for lvl, role_id in sorted(rewards.items(), key=lambda x: int(x[0])):
            role = interaction.guild.get_role(role_id)
            embed.add_field(name=f"المستوى {lvl}", value=role.mention if role else "رتبة محذوفة", inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="remove-role-reward", description="حذف مكافأة مستوى")
    @app_commands.describe(level="المستوى")
    @app_commands.checks.has_permissions(administrator=True)
    async def remove_role_reward(self, interaction: discord.Interaction, level: int):
        data = load_rewards()
        gid = str(interaction.guild.id)
        if gid in data and str(level) in data[gid]:
            del data[gid][str(level)]
            save_rewards(data)
            await interaction.response.send_message(f"✅ تم حذف مكافأة المستوى **{level}**")
        else:
            await interaction.response.send_message("❌ لا توجد مكافأة لهذا المستوى!", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        data = load_levels()
        rewards = load_rewards()
        gid, uid = str(message.guild.id), str(message.author.id)
        if gid not in data: data[gid] = {}
        if uid not in data[gid]: data[gid][uid] = {"xp": 0, "level": 0}
        multiplier = data[gid].get("xp_multiplier", 1.0)
        gained = int(random.randint(15, 25) * multiplier)
        data[gid][uid]["xp"] += gained
        current_level = data[gid][uid]["level"]
        needed = 5 * (current_level ** 2) + 50 * current_level + 100
        if data[gid][uid]["xp"] >= needed:
            data[gid][uid]["xp"] -= needed
            data[gid][uid]["level"] += 1
            new_level = data[gid][uid]["level"]
            reward_role_id = rewards.get(gid, {}).get(str(new_level))
            if reward_role_id:
                role = message.guild.get_role(reward_role_id)
                if role:
                    try:
                        await message.author.add_roles(role)
                        await message.channel.send(f"🎉 {message.author.mention} وصل للمستوى **{new_level}** وحصل على رتبة {role.mention}!")
                    except:
                        pass
            else:
                await message.channel.send(f"🎉 {message.author.mention} وصل للمستوى **{new_level}**!")
        save_levels(data)

async def setup(bot):
    await bot.add_cog(AdvancedLevels(bot))
