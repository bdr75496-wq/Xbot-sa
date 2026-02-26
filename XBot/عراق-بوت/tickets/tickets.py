import discord
from discord import app_commands
from discord.ext import commands
import json, os

def load_tickets():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists("data/tickets.json"):
        return {}
    with open("data/tickets.json", "r") as f:
        return json.load(f)

def save_tickets(data):
    with open("data/tickets.json", "w") as f:
        json.dump(data, f, indent=4)

class TicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="فتح تذكرة 🎫", style=discord.ButtonStyle.green, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        data = load_tickets()
        uid = str(interaction.user.id)

        for ch in guild.text_channels:
            if ch.name == f"تذكرة-{interaction.user.name}":
                return await interaction.response.send_message("❌ عندك تذكرة مفتوحة بالفعل!", ephemeral=True)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True)
        }

        channel = await guild.create_text_channel(f"تذكرة-{interaction.user.name}", overwrites=overwrites)

        embed = discord.Embed(title="🎫 تذكرة مفتوحة", description=f"مرحباً {interaction.user.mention}!\nسيقوم الفريق بمساعدتك قريباً.", color=discord.Color.green())
        close_view = CloseTicketView()
        await channel.send(embed=embed, view=close_view)

        data[str(channel.id)] = {"user_id": uid, "status": "open"}
        save_tickets(data)

        await interaction.response.send_message(f"✅ تم فتح تذكرتك: {channel.mention}", ephemeral=True)

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="إغلاق التذكرة 🔒", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.channel.edit(name=f"مغلقة-{interaction.channel.name}")
        await interaction.response.send_message("🔒 تم إغلاق التذكرة")
        data = load_tickets()
        data[str(interaction.channel.id)]["status"] = "closed"
        save_tickets(data)

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ticket-panel", description="إنشاء بانل التذاكر")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def ticket_panel(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🎫 نظام التذاكر", description="اضغط على الزر لفتح تذكرة دعم", color=discord.Color.blue())
        await interaction.channel.send(embed=embed, view=TicketButton())
        await interaction.response.send_message("✅ تم إنشاء البانل!", ephemeral=True)

    @app_commands.command(name="ticket-open", description="فتح تذكرة يدوياً")
    async def ticket_open(self, interaction: discord.Interaction):
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True)
        }
        channel = await guild.create_text_channel(f"تذكرة-{interaction.user.name}", overwrites=overwrites)
        embed = discord.Embed(title="🎫 تذكرة مفتوحة", description=f"مرحباً {interaction.user.mention}!", color=discord.Color.green())
        await channel.send(embed=embed, view=CloseTicketView())
        await interaction.response.send_message(f"✅ تم فتح تذكرتك: {channel.mention}", ephemeral=True)

    @app_commands.command(name="ticket-close", description="إغلاق التذكرة الحالية")
    async def ticket_close(self, interaction: discord.Interaction):
        if "تذكرة" not in interaction.channel.name:
            return await interaction.response.send_message("❌ هذه ليست قناة تذكرة!", ephemeral=True)
        await interaction.channel.edit(name=f"مغلقة-{interaction.channel.name}")
        await interaction.response.send_message("🔒 تم إغلاق التذكرة")

    @app_commands.command(name="ticket-add", description="إضافة عضو للتذكرة")
    @app_commands.describe(member="العضو")
    async def ticket_add(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.channel.set_permissions(member, read_messages=True, send_messages=True)
        await interaction.response.send_message(f"✅ تم إضافة {member.mention}")

    @app_commands.command(name="ticket-remove", description="إزالة عضو من التذكرة")
    @app_commands.describe(member="العضو")
    async def ticket_remove(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.channel.set_permissions(member, read_messages=False)
        await interaction.response.send_message(f"✅ تم إزالة {member.mention}")

    @app_commands.command(name="ticket-rename", description="تغيير اسم التذكرة")
    @app_commands.describe(name="الاسم الجديد")
    async def ticket_rename(self, interaction: discord.Interaction, name: str):
        await interaction.channel.edit(name=name)
        await interaction.response.send_message(f"✅ تم تغيير الاسم إلى: {name}")

    @app_commands.command(name="ticket-delete", description="حذف التذكرة نهائياً")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def ticket_delete(self, interaction: discord.Interaction):
        await interaction.response.send_message("🗑️ سيتم حذف القناة خلال 5 ثواني...")
        import asyncio
        await asyncio.sleep(5)
        await interaction.channel.delete()

    @app_commands.command(name="ticket-info", description="معلومات التذكرة")
    async def ticket_info(self, interaction: discord.Interaction):
        data = load_tickets()
        info = data.get(str(interaction.channel.id))
        if not info:
            return await interaction.response.send_message("❌ هذه ليست قناة تذكرة!", ephemeral=True)
        embed = discord.Embed(title="🎫 معلومات التذكرة", color=discord.Color.blue())
        embed.add_field(name="الحالة", value=info["status"])
        embed.add_field(name="ID القناة", value=interaction.channel.id)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ticket-reopen", description="إعادة فتح تذكرة مغلقة")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def ticket_reopen(self, interaction: discord.Interaction):
        new_name = interaction.channel.name.replace("مغلقة-", "")
        await interaction.channel.edit(name=new_name)
        await interaction.response.send_message("✅ تم إعادة فتح التذكرة")

    @app_commands.command(name="ticket-transfer", description="نقل التذكرة لمشرف آخر")
    @app_commands.describe(member="المشرف الجديد")
    async def ticket_transfer(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.channel.set_permissions(member, read_messages=True, send_messages=True)
        await interaction.response.send_message(f"✅ تم نقل التذكرة إلى {member.mention}")

async def setup(bot):
    await bot.add_cog(Tickets(bot))
