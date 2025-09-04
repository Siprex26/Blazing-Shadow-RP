import discord
from discord.ext import commands
import os

# ----- CONFIGURACIÓN DE INTENTS -----
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ----- LISTAS DE ROLES -----
aldeas = [
    "⛈𝕃𝕃𝕌𝕍𝕀𝔸🌧", "🌿ℍ𝕀𝔼ℝ𝔹𝔸🌿", "🌫ℕ𝕀𝔼𝔹𝕃𝔸🌫",
    "🌳𝕂𝕆ℕ𝕆ℍ𝔸🍃", "☁ℕ𝕌𝔹𝔼☁", "🎶𝕊𝕆ℕ𝕀𝔻𝕆🎶",
    "⌛𝔸ℝ𝔼ℕ𝔸⏳", "🗻ℝ𝕆ℂ𝔸🗻"
]

# Límite general para aldeas
LIMITE_ALDEAS = 6

# LÍMITES INDIVIDUALES PARA CADA CLAN
clanes_limites = {
    "Uchiha┃👁️": 5,
    "Hyuga┃👁": 4,
    "Senju ┃千住": 3,
    "Aburame┃🐜": 5,
    "INUZUKA ┃🐩": 5,
    "Uzumaki ┃🎴": 5,
    "Lee┃🦶": 4,
    "Namikaze┃🎇": 4
}

# ----- EVENTO DE INICIO -----
@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

# ----- COMANDO ALDEAS -----
@bot.command()
async def aldeas(ctx):
    mensaje = "**📜 Aldeas:**\n"
    for nombre in aldeas:
        role = discord.utils.get(ctx.guild.roles, name=nombre)
        if role:
            count = len(role.members)
            mensaje += f"{nombre}: {count}/{LIMITE_ALDEAS}\n"
        else:
            mensaje += f"{nombre}: ❌ Rol no encontrado\n"
    await ctx.send(mensaje)

# ----- COMANDO CLANES -----
@bot.command()
async def clanes(ctx):
    mensaje = "**👥 Clanes:**\n"
    for nombre, limite in clanes_limites.items():
        role = discord.utils.get(ctx.guild.roles, name=nombre)
        if role:
            count = len(role.members)
            estado = "🔴 **LLENO**" if count >= limite else "🟢"
            mensaje += f"{nombre}: {count}/{limite} {estado}\n"
        else:
            mensaje += f"{nombre}: ❌ Rol no encontrado\n"
    await ctx.send(mensaje)

# ----- INICIAR BOT -----
bot.run(os.getenv("DISCORD_TOKEN"))
