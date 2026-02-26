import discord
from discord import app_commands
from discord.ext import commands
import json, os

def load_applies():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists("data/applies.json"):
        return {}
    with open("data/applies.json", "r") as f:
        return json.load(f)

def save_applies(data):
    with open("data/applies.json", "w") as f:
        json.dump(data, f, indent=4)

class ApplyModal(discord.ui.Modal, title="نموذج التقديم"):
    reason = discord.ui.TextInput(label="لماذا تريد التقديم؟", style=discord.TextStyle.paragraph)
    experience = discord.ui.TextInput(label="ما هي خبرتك؟", style=discord.TextStyle.paragraph)
    age = discord.ui.TextInput(label="كم عمرك؟", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        data = load_applies()
        uid = str(interaction.user.id)
        data[uid] = {
            "reason": str(self.reason),
            "experience": str(self.experience),
            "age": str(self.age),
            "status": "pending"
        }
        save_applies(data)

        log_channel = discord.utils.get(interaction.guild.text_channels, name="تقديمات")
        if log_channel:
            embed = discord.Embed(title="📋 تقديم جديد", color=discord.Color.blue())
            embed.add_field(name="العضو", value=interaction.user.mention)
            embed.add_field(name="السبب", value=str(self.reason), inline=False)
            embed.add_field(name="الخبرة", value=str(self.experience), inline=False)
            embed.add_field(name="العمر", value=str(self.age))
            await log_channel.send(embed=embed)

        await interaction.response.send_message("✅ تم إرسال تقديمك بنجاح!", ephemeral=True)

class ApplyButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="تقدم الآن 📋", style=discord.ButtonStyle.blurple, custom_id="apply_btn")
    async def apply(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ApplyModal())

class Apply(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="apply-panel", description="إرسال بانل التقديم")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def apply_panel(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📋 نظام التقديم", description="اضغط على الزر للتقديم", color=discord.Color.blue())
        await interaction.channel.send(embed=embed, view=ApplyButton())
        await interaction.response.send_message("✅ تم إنشاء البانل!", ephemeral=True)

    @app_commands.command(name="apply-accept", description="قبول تقديم عضو")
    @app_commands.describe(member="العضو")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def apply_accept(self, interaction: discord.Interaction, member: discord.Member):
        data = load_applies()
        uid = str(member.id)
        if uid in data:
            data[uid]["status"] = "accepted"
            save_applies(data)
        await member.send("🎉 تم قبول تقديمك!")
        embed = discord.Embed(title="✅ تم القبول", color=discord.Color.green())
        embed.add_field(name="العضو", value=member.mention)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="apply-reject", description="رفض تقديم عضو")
    @app_commands.describe(member="العضو", reason="السبب")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def apply_reject(self, interaction: discord.Interaction, member: discord.Member, reason: str = "بدون سبب"):
        data = load_applies()
        uid = str(member.id)
        if uid in data:
            data[uid]["status"] = "rejected"
            save_applies(data)
        await member.send(f"❌ تم رفض تقديمك. السبب: {reason}")
        embed = discord.Embed(title="❌ تم الرفض", color=discord.Color.red())
        embed.add_field(name="العضو", value=member.mention)
        embed.add_field(name="السبب", value=reason)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Apply(bot))
