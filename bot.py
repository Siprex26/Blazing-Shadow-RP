import discord
from discord.ext import commands, tasks
import os
from datetime import datetime, timedelta
import actividad
import lives

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

LIMITE_ALDEAS = 6

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

# ----- INACTIVIDAD -----
ultimo_mensaje = actividad.ultimo_mensaje
ROL_INACTIVO = "inactivo"
DIAS_INACTIVO = 3
ARCHIVO_ACTIVIDAD = "actividad.py"

# ----- FUNCIONES PARA GUARDAR -----
def guardar_actividad():
    with open(ARCHIVO_ACTIVIDAD, "w") as f:
        f.write("from datetime import datetime\n\n")
        f.write("ultimo_mensaje = {\n")
        for k, v in ultimo_mensaje.items():
            f.write(f"    {k}: datetime({v.year}, {v.month}, {v.day}, {v.hour}, {v.minute}, {v.second}),\n")
        f.write("}\n")

def guardar_lives():
    with open("lives.py", "w") as f:
        f.write("from datetime import datetime\n\n")
        f.write("lives = [\n")
        for l in lives.lives:
            f.write(f"    {{'nombre': '{l['nombre']}', 'fecha': datetime({l['fecha'].year}, {l['fecha'].month}, {l['fecha'].day}), 'confirmado': '{l['confirmado']}', 'estado': '{l['estado']}' }},\n")
        f.write("]\n")

# ----- EVENTO DE INICIO -----
@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    guild = bot.guilds[0]
    for miembro in guild.members:
        if not miembro.bot and miembro.id not in ultimo_mensaje:
            ultimo_mensaje[miembro.id] = datetime.utcnow()
    revisar_inactividad.start()

# ----- GUARDAR ACTIVIDAD AL ENVIAR MENSAJE -----
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    ultimo_mensaje[message.author.id] = datetime.utcnow()
    guardar_actividad()
    await bot.process_commands(message)

# ----- TAREA DE INACTIVIDAD -----
@tasks.loop(hours=1)
async def revisar_inactividad():
    ahora = datetime.utcnow()
    guild = bot.guilds[0]
    rol_inactivo = discord.utils.get(guild.roles, name=ROL_INACTIVO)
    if not rol_inactivo:
        print(f"⚠️ No se encontró el rol {ROL_INACTIVO}")
        return

    for miembro in guild.members:
        if miembro.bot:
            continue

        ultima = ultimo_mensaje.get(miembro.id)
        if not ultima:
            ultimo_mensaje[miembro.id] = datetime.utcnow()
            guardar_actividad()
            ultima = ultimo_mensaje[miembro.id]

        if ahora - ultima > timedelta(days=DIAS_INACTIVO):
            if rol_inactivo not in miembro.roles:
                await miembro.add_roles(rol_inactivo)
                try:
                    await miembro.send(
                        f"⚠️ Hola {miembro.name}, has sido marcado como inactivo. "
                        "Envía un mensaje en el servidor para quitar el rol y seguir participando."
                    )
                except:
                    print(f"No se pudo enviar mensaje a {miembro.name}")
        else:
            if rol_inactivo in miembro.roles:
                await miembro.remove_roles(rol_inactivo)

# ----- COMANDOS -----
@bot.command(help="Muestra los miembros inactivos en el servidor")
async def inactivos(ctx):
    guild = ctx.guild
    rol_inactivo = discord.utils.get(guild.roles, name=ROL_INACTIVO)
    if not rol_inactivo:
        await ctx.send(f"⚠️ No se encontró el rol {ROL_INACTIVO}")
        return

    miembros_inactivos = [m.mention for m in rol_inactivo.members]
    if miembros_inactivos:
        await ctx.send("📋 Miembros inactivos:\n" + "\n".join(miembros_inactivos))
    else:
        await ctx.send("✅ No hay miembros inactivos actualmente.")

@bot.command(help="Muestra todas las aldeas y cuántos miembros tienen")
async def aldeas_cmd(ctx):
    mensaje = "**📜 Aldeas:**\n"
    for nombre_rol in aldeas:
        role = discord.utils.get(ctx.guild.roles, name=nombre_rol)
        if role:
            count = len(role.members)
            mensaje += f"{nombre_rol}: {count}/{LIMITE_ALDEAS}\n"
        else:
            mensaje += f"{nombre_rol}: ❌ Rol no encontrado\n"
    await ctx.send(mensaje)

@bot.command(help="Muestra todos los clanes y su estado de ocupación")
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

@bot.command(help="Muestra todos los comandos disponibles")
async def cmds(ctx):
    mensaje = "**📜 Comandos disponibles:**\n"
    for comando in bot.commands:
        descripcion = comando.help if comando.help else "Sin descripción"
        mensaje += f"- !{comando.name}: {descripcion}\n"
    await ctx.send(mensaje)

# ----- COMANDOS DE LIVES -----
@bot.command(help="Crea un live. Solo admins")
@commands.has_permissions(administrator=True)
async def create_live(ctx, *, info: str):
    try:
        partes = {k.strip().lower(): v.strip() for k, v in (item.split(":",1) for item in info.split(" ") if ":" in item)}
    except:
        await ctx.send("❌ Formato incorrecto. Usa: nombre: <nombre> Fecha: <dd/mm/aa> Confirmado: <si/no/probable>")
        return

    nombre = partes.get("nombre", "Sin nombre")
    fecha_str = partes.get("fecha", None)
    confirmado = partes.get("confirmado", "sin confirmar").lower()

    try:
        fecha = datetime.strptime(fecha_str, "%d/%m/%y")
    except:
        await ctx.send("❌ Fecha inválida. Usa formato dd/mm/aa")
        return

    lives.lives.append({
        "nombre": nombre,
        "fecha": fecha,
        "confirmado": confirmado,
        "estado": "pendiente"
    })
    guardar_lives()
    await ctx.send(f"✅ Live `{nombre}` creado para el {fecha_str} ({confirmado})")

@bot.command(help="Marca un live como en vivo. Solo admins")
@commands.has_permissions(administrator=True)
async def start_live(ctx, *, info: str):
    try:
        partes = {k.strip().lower(): v.strip() for k, v in (item.split(":",1) for item in info.split(" ") if ":" in item)}
        nombre = partes.get("nombre")
    except:
        await ctx.send("❌ Formato incorrecto. Usa: nombre: <nombre>")
        return

    for live in lives.lives:
        if live["nombre"].lower() == nombre.lower():
            live["estado"] = "en vivo"
            guardar_lives()
            await ctx.send(f"✅ Live `{nombre}` ahora está **en vivo**")
            return

    await ctx.send("❌ No se encontró un live con ese nombre.")

@bot.command(help="Muestra los lives en vivo y próximos")
async def lives_cmd(ctx):
    ahora = datetime.now()
    embed = discord.Embed(title="📺 Lives", color=0x1abc9c)

    # Lives en vivo
    en_vivo = [l for l in lives.lives if l["estado"] == "en vivo"]
    if en_vivo:
        texto_vivo = ""
        for l in en_vivo:
            texto_vivo += f"🔥 **{l['nombre']}** - Confirmado: {l['confirmado']}\n"
        embed.add_field(name="En Vivo", value=texto_vivo, inline=False)

    # Próximos lives desde mañana
    proximos = [l for l in lives.lives if l["estado"] != "en vivo" and l["fecha"] >= (ahora + timedelta(days=1))]
    if proximos:
        texto_prox = ""
        for l in sorted(proximos, key=lambda x: x["fecha"]):
            texto_prox += f"⏳ {l['nombre']} - {l['fecha'].strftime('%d/%m/%y')} - Confirmado: {l['confirmado']}\n"
        embed.add_field(name="Próximos Lives", value=texto_prox, inline=False)

    if not en_vivo and not proximos:
        embed.description = "No hay lives programados."

    await ctx.send(embed=embed)

# ----- INICIAR BOT -----
bot.run(os.getenv("DISCORD_TOKEN"))
