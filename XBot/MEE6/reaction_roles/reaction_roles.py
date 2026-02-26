import discord
from discord.ext import commands
from discord import app_commands

reaction_roles = {}

class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="reactionrole", description="ربط إيموجي بدور تلقائي")
    @app_commands.describe(message_id="الرقم التعريفي للرسالة", emoji="الإيموجي", role="الدور")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def reactionrole(self, interaction: discord.Interaction, message_id: str, emoji: str, role: discord.Role):
        if message_id not in reaction_roles:
            reaction_roles[message_id] = {}
        reaction_roles[message_id][emoji] = role.id
        try:
            msg = await interaction.channel.fetch_message(int(message_id))
            await msg.add_reaction(emoji)
        except:
            pass
        embed = discord.Embed(title="✅ تم ربط الدور", color=discord.Color.green())
        embed.add_field(name="الإيموجي", value=emoji)
        embed.add_field(name="الدور", value=role.mention)
        await interaction.response.send_message(embed=embed)

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
