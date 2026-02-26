import discord
from discord.ext import commands
from discord import app_commands
import json, os

def load_tags():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists("data/carlbot_tags.json"):
        return {}
    with open("data/carlbot_tags.json", "r") as f:
        return json.load(f)

def save_tags(data):
    with open("data/carlbot_tags.json", "w") as f:
        json.dump(data, f, indent=4)

class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="tag-create", description="إنشاء رد جاهز (تاق)")
    @app_commands.describe(name="اسم التاق", content="المحتوى")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def tag_create(self, interaction: discord.Interaction, name: str, content: str):
        data = load_tags()
        gid = str(interaction.guild.id)
        if gid not in data:
            data[gid] = {}
        data[gid][name.lower()] = {"content": content, "author": str(interaction.user.id)}
        save_tags(data)
        await interaction.response.send_message(f"✅ تم إنشاء التاق: **{name}**\nاستخدمه بـ `/tag {name}`")

    @app_commands.command(name="tag-edit", description="تعديل رد جاهز")
    @app_commands.describe(name="اسم التاق", content="المحتوى الجديد")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def tag_edit(self, interaction: discord.Interaction, name: str, content: str):
        data = load_tags()
        gid = str(interaction.guild.id)
        if gid in data and name.lower() in data[gid]:
            data[gid][name.lower()]["content"] = content
            save_tags(data)
            await interaction.response.send_message(f"✅ تم تعديل التاق: **{name}**")
        else:
            await interaction.response.send_message("❌ التاق غير موجود!", ephemeral=True)

    @app_commands.command(name="tag-delete", description="حذف رد جاهز")
    @app_commands.describe(name="اسم التاق")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def tag_delete(self, interaction: discord.Interaction, name: str):
        data = load_tags()
        gid = str(interaction.guild.id)
        if gid in data and name.lower() in data[gid]:
            del data[gid][name.lower()]
            save_tags(data)
            await interaction.response.send_message(f"✅ تم حذف التاق: **{name}**")
        else:
            await interaction.response.send_message("❌ التاق غير موجود!", ephemeral=True)

    @app_commands.command(name="tag", description="استدعاء رد جاهز")
    @app_commands.describe(name="اسم التاق")
    async def tag(self, interaction: discord.Interaction, name: str):
        data = load_tags()
        gid = str(interaction.guild.id)
        tag = data.get(gid, {}).get(name.lower())
        if not tag:
            await interaction.response.send_message("❌ التاق غير موجود!", ephemeral=True)
            return
        content = tag["content"]
        content = content.replace("{user}", interaction.user.mention)
        content = content.replace("{server}", interaction.guild.name)
        content = content.replace("{count}", str(interaction.guild.member_count))
        await interaction.response.send_message(content)

    @app_commands.command(name="tag-list", description="عرض جميع التاقز")
    async def tag_list(self, interaction: discord.Interaction):
        data = load_tags()
        gid = str(interaction.guild.id)
        tags = data.get(gid, {})
        if not tags:
            await interaction.response.send_message("❌ لا توجد تاقز بعد.")
            return
        embed = discord.Embed(title="🔧 قائمة التاقز", color=discord.Color.blue())
        for name in tags:
            embed.add_field(name=f"/{name}", value=tags[name]["content"][:50] + "...", inline=False)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Tags(bot))
