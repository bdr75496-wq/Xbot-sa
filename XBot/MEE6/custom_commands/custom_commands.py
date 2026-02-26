import discord
from discord.ext import commands
from discord import app_commands

custom_commands = {}

class CustomCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="addcommand", description="إضافة أمر مخصص")
    @app_commands.describe(name="اسم الأمر", response="رد الأمر")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def addcommand(self, interaction: discord.Interaction, name: str, response: str):
        gid = str(interaction.guild.id)
        if gid not in custom_commands:
            custom_commands[gid] = {}
        custom_commands[gid][name.lower()] = response
        await interaction.response.send_message(f"✅ تم إضافة الأمر: **!{name}**")

    @app_commands.command(name="delcommand", description="حذف أمر مخصص")
    @app_commands.describe(name="اسم الأمر")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def delcommand(self, interaction: discord.Interaction, name: str):
        gid = str(interaction.guild.id)
        if gid in custom_commands and name.lower() in custom_commands[gid]:
            del custom_commands[gid][name.lower()]
            await interaction.response.send_message(f"✅ تم حذف الأمر: **!{name}**")
        else:
            await interaction.response.send_message("❌ الأمر غير موجود!", ephemeral=True)

    @app_commands.command(name="listcommands", description="عرض جميع الأوامر المخصصة")
    async def listcommands(self, interaction: discord.Interaction):
        gid = str(interaction.guild.id)
        cmds = custom_commands.get(gid, {})
        if not cmds:
            await interaction.response.send_message("❌ لا توجد أوامر مخصصة بعد.")
            return
        embed = discord.Embed(title="📋 الأوامر المخصصة", color=discord.Color.blue())
        for name, resp in cmds.items():
            embed.add_field(name=f"!{name}", value=resp[:100], inline=False)
        await interaction.response.send_message(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        gid = str(message.guild.id)
        cmds = custom_commands.get(gid, {})
        content = message.content.lower().strip()
        for name, response in cmds.items():
            if content == f"!{name}":
                response = response.replace("{user}", message.author.mention)
                response = response.replace("{server}", message.guild.name)
                response = response.replace("{count}", str(message.guild.member_count))
                await message.channel.send(response)
                break

async def setup(bot):
    await bot.add_cog(CustomCommands(bot))
