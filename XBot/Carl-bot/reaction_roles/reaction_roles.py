import discord
from discord.ext import commands
from discord import app_commands

reaction_roles = {}

class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="rr-create", description="إنشاء رسالة رتب تفاعلية")
    @app_commands.describe(title="عنوان الرسالة", description="وصف الرسالة")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def rr_create(self, interaction: discord.Interaction, title: str, description: str):
        embed = discord.Embed(title=f"🎭 {title}", description=description, color=discord.Color.blue())
        embed.set_footer(text="تفاعل بالإيموجي للحصول على الرتبة")
        msg = await interaction.channel.send(embed=embed)
        reaction_roles[str(msg.id)] = {}
        await interaction.response.send_message(f"✅ تم إنشاء رسالة الرتب! الرقم التعريفي: `{msg.id}`\nاستخدم `/rr-add` لإضافة رتب.", ephemeral=True)

    @app_commands.command(name="rr-add", description="إضافة رتبة لرسالة تفاعلية")
    @app_commands.describe(message_id="الرقم التعريفي للرسالة", emoji="الإيموجي", role="الرتبة")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def rr_add(self, interaction: discord.Interaction, message_id: str, emoji: str, role: discord.Role):
        if message_id not in reaction_roles:
            reaction_roles[message_id] = {}
        reaction_roles[message_id][emoji] = role.id
        try:
            msg = await interaction.channel.fetch_message(int(message_id))
            await msg.add_reaction(emoji)
            # تحديث الـ embed
            old_embed = msg.embeds[0]
            new_embed = discord.Embed(title=old_embed.title, description=old_embed.description, color=old_embed.color)
            for field in old_embed.fields:
                new_embed.add_field(name=field.name, value=field.value, inline=field.inline)
            new_embed.add_field(name=emoji, value=role.mention, inline=True)
            new_embed.set_footer(text="تفاعل بالإيموجي للحصول على الرتبة")
            await msg.edit(embed=new_embed)
        except:
            pass
        await interaction.response.send_message(f"✅ تم ربط {emoji} بـ {role.mention}", ephemeral=True)

    @app_commands.command(name="rr-delete", description="حذف نظام الرتب التفاعلية")
    @app_commands.describe(message_id="الرقم التعريفي للرسالة")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def rr_delete(self, interaction: discord.Interaction, message_id: str):
        if message_id in reaction_roles:
            del reaction_roles[message_id]
        try:
            msg = await interaction.channel.fetch_message(int(message_id))
            await msg.delete()
        except:
            pass
        await interaction.response.send_message("✅ تم حذف نظام الرتب التفاعلية.", ephemeral=True)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        mid = str(payload.message_id)
        if mid not in reaction_roles:
            return
        emoji = str(payload.emoji)
        if emoji not in reaction_roles[mid]:
            return
        guild = self.bot.get_guild(payload.guild_id)
        role = guild.get_role(reaction_roles[mid][emoji])
        member = guild.get_member(payload.user_id)
        if role and member and not member.bot:
            await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        mid = str(payload.message_id)
        if mid not in reaction_roles:
            return
        emoji = str(payload.emoji)
        if emoji not in reaction_roles[mid]:
            return
        guild = self.bot.get_guild(payload.guild_id)
        role = guild.get_role(reaction_roles[mid][emoji])
        member = guild.get_member(payload.user_id)
        if role and member:
            await member.remove_roles(role)

async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))
