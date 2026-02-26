import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class AutoMessages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tasks = {}

    @app_commands.command(name="automessage", description="إضافة رسالة تلقائية مجدولة")
    @app_commands.describe(channel="الروم", message="الرسالة", minutes="كل كم دقيقة")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def automessage(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str, minutes: int):
        async def send_loop():
            while True:
                await asyncio.sleep(minutes * 60)
                ch = self.bot.get_channel(channel.id)
                if ch:
                    await ch.send(message)

        key = f"{interaction.guild.id}_{channel.id}"
        if key in self.tasks:
            self.tasks[key].cancel()
        self.tasks[key] = self.bot.loop.create_task(send_loop())
        embed = discord.Embed(title="✅ تم إعداد الرسالة التلقائية", color=discord.Color.green())
        embed.add_field(name="الروم", value=channel.mention)
        embed.add_field(name="كل", value=f"{minutes} دقيقة")
        embed.add_field(name="الرسالة", value=message[:100], inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="stopauto", description="إيقاف الرسائل التلقائية في روم")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def stopauto(self, interaction: discord.Interaction, channel: discord.TextChannel):
        key = f"{interaction.guild.id}_{channel.id}"
        if key in self.tasks:
            self.tasks[key].cancel()
            del self.tasks[key]
            await interaction.response.send_message(f"✅ تم إيقاف الرسائل التلقائية في {channel.mention}")
        else:
            await interaction.response.send_message("❌ لا توجد رسائل تلقائية في هذا الروم!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AutoMessages(bot))
