import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Listas renombradas
aldeas_list = ["⛈𝕃𝕃𝕌𝕍𝕀𝔸🌧", "🌿ℍ𝕀𝔼ℝ𝔹𝔸🌿", "🌫ℕ𝕀𝔼𝔹𝕃𝔸🌫", "🌳𝕂𝕆ℕ𝕆ℍ𝔸🍃", "☁ℕ𝕌𝔹𝔼☁", "🎶𝕊𝕆ℕ𝕀𝔻𝕆🎶", "⌛𝔸ℝ𝔼ℕ𝔸⏳", "🗻ℝ𝕆ℂ𝔸🗻"]
clanes_list = ["Uchiha┃👁️", "Hyuga┃👁", "Senju ┃千住", "Aburame┃🐜", "INUZUKA ┃🐩", "Uzumaki ┃🎴", "Lee┃🦶", "Namikaze┃🎇"]

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

@bot.command()
async def aldeas(ctx):
    mensaje = "**📜 Aldeas:**\n"
    for nombre in aldeas_list:
        role = discord.utils.get(ctx.guild.roles, name=nombre)
        if role:
            mensaje += f"{nombre}: {len(role.members)}/6\n"
        else:
            mensaje += f"{nombre}: ❌ Rol no encontrado\n"
    await ctx.send(mensaje)

@bot.command()
async def clanes(ctx):
    mensaje = "**👥 Clanes:**\n"
    for nombre in clanes_list:
        role = discord.utils.get(ctx.guild.roles, name=nombre)
        if role:
            mensaje += f"{nombre}: {len(role.members)} miembros\n"
        else:
            mensaje += f"{nombre}: ❌ Rol no encontrado\n"
    await ctx.send(mensaje)

bot.run(os.getenv("DISCORD_TOKEN"))
