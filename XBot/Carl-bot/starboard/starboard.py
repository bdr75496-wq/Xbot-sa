import discord
from discord.ext import commands
from discord import app_commands
import json, os

def load_starboard():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists("data/starboard.json"):
        return {}
    with open("data/starboard.json", "r") as f:
        return json.load(f)

def save_starboard(data):
    with open("data/starboard.json", "w") as f:
        json.dump(data, f, indent=4)

class Starboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.posted = {}

    @app_commands.command(name="starboard-setup", description="إعداد نظام النجوم")
    @app_commands.describe(channel="روم الستاربورد", stars="عدد النجوم المطلوب")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def starboard_setup(self, interaction: discord.Interaction, channel: discord.TextChannel, stars: int = 3):
        data = load_starboard()
        gid = str(interaction.guild.id)
        data[gid] = {"channel": channel.id, "stars": stars}
        save_starboard(data)
        embed = discord.Embed(title="⭐ تم إعداد الستاربورد", color=discord.Color.gold())
        embed.add_field(name="الروم", value=channel.mention)
        embed.add_field(name="النجوم المطلوبة", value=str(stars))
        await interaction.response.send_message(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if str(payload.emoji) != "⭐":
            return
        data = load_starboard()
        gid = str(payload.guild_id)
        if gid not in data:
            return
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        try:
            message = await channel.fetch_message(payload.message_id)
        except:
            return
        reaction = discord.utils.get(message.reactions, emoji="⭐")
        if not reaction:
            return
        required = data[gid]["stars"]
        if reaction.count < required:
            return
        msg_id = str(payload.message_id)
        if msg_id in self.posted:
            return
        self.posted[msg_id] = True
        star_channel = guild.get_channel(data[gid]["channel"])
        if not star_channel:
            return
        embed = discord.Embed(description=message.content, color=discord.Color.gold())
        embed.add_field(name="الرابط", value=f"[اضغط هنا]({message.jump_url})")
        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
        embed.set_footer(text=f"⭐ {reaction.count} نجمة | #{channel.name}")
        if message.attachments:
            embed.set_image(url=message.attachments[0].url)
        await star_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Starboard(bot))
