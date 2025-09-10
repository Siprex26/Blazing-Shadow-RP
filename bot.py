import discord
from discord.ext import commands, tasks
import os
from datetime import datetime, timedelta
import actividad
import json

# ----- CONFIGURACIÓN DE INTENTS -----
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ----- LISTAS DE ROLES -----
aldeas_list = [
    "⛈𝕃𝕃𝕌𝕍𝕀𝔸🌧", "🌿ℍ𝕀𝔼ℝ𝔹𝔸🌿", "🌫ℕ𝕀𝔼𝔹𝕃𝔸🌫",
    "🌳𝕂𝕆ℕ𝕆ℍ𝔸🍃", "☁ℕ𝕌𝔹𝔼☁", "🎶𝕊𝕆ℕ𝕀𝔻𝕆🎶",
    "⌛𝔸ℝ𝔼ℕ𝔸⏳", "🗻ℝ𝕆ℂ𝔸🗻"
]

LIMITE_ALDEAS = 6

clanes_limites = {
    "Uchiha┃👁️": 5,
    "Hyuga┃👁": 4,
    "Senju ┃千住": 3,
    "Aburame┃🐜": 4,
    "INUZUKA ┃🐩": 4,
    "Uzumaki ┃🎴": 3,
    "Lee┃🦶": 3,
    "Namikaze┃🎇": 4,
    "Akimichi": 5,
    "Sarutobi": 4,
    "Hatake": 4,
}

# ----- INACTIVIDAD -----
ultimo_mensaje = actividad.ultimo_mensaje
ROL_INACTIVO = "inactivo"
DIAS_INACTIVO = 3
ARCHIVO_ACTIVIDAD = "actividad.py"

def guardar_actividad():
    with open(ARCHIVO_ACTIVIDAD, "w") as f:
        f.write("from datetime import datetime\n\n")
        f.write("ultimo_mensaje = {\n")
        for k, v in ultimo_mensaje.items():
            f.write(f"    {k}: datetime({v.year}, {v.month}, {v.day}, {v.hour}, {v.minute}, {v.second}),\n")
        f.write("}\n")

# ----- LIVES -----
LIVES_FILE = "lives.json"

def cargar_lives():
    if os.path.exists(LIVES_FILE):
        with open(LIVES_FILE, "r") as f:
            return json.load(f)
    return []

def guardar_lives(lives):
    with open(LIVES_FILE, "w") as f:
        json.dump(lives, f, indent=4)

lives_list = cargar_lives()

# ----- EVENTOS -----
@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    guild = bot.guilds[0]
    for miembro in guild.members:
        if not miembro.bot and miembro.id not in ultimo_mensaje:
            ultimo_mensaje[miembro.id] = datetime.utcnow()
    revisar_inactividad.start()

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
                    await miembro.send(f"⚠️ Hola {miembro.name}, has sido marcado como inactivo. Envía un mensaje para quitar el rol.")
                except:
                    print(f"No se pudo enviar mensaje a {miembro.name}")
        else:
            if rol_inactivo in miembro.roles:
                await miembro.remove_roles(rol_inactivo)

# ----- COMANDOS -----
@bot.command()
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

@bot.command()
async def aldeas(ctx):
    mensaje = "**📜 Aldeas:**\n"
    for nombre in aldeas_list:
        role = discord.utils.get(ctx.guild.roles, name=nombre)
        if role:
            count = len(role.members)
            mensaje += f"{nombre}: {count}/{LIMITE_ALDEAS}\n"
        else:
            mensaje += f"{nombre}: ❌ Rol no encontrado\n"
    await ctx.send(mensaje)

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

@bot.command()
async def cmds(ctx):
    mensaje = "**📜 Comandos Disponibles:**\n"
    cmds_list = [
        "!aldeas",
        "!clanes",
        "!inactivos",
        "!cmds",
        "!create-live nombre:X fecha:dd/mm/aa confirmado:si/no/probable (Admin)",
        "!start-live nombre:X (Admin)",
        "!lives"
    ]
    mensaje += "\n".join(cmds_list)
    await ctx.send(mensaje)

@bot.command()
@commands.has_permissions(administrator=True)
async def create_live(ctx, *, info: str):
    partes = {}
    for item in info.split():
        if ":" in item:
            k, v = item.split(":", 1)
            partes[k.strip().lower()] = v.strip()
    nombre = partes.get("nombre", "Sin nombre")
    fecha_str = partes.get("fecha", None)
    confirmado = partes.get("confirmado", "sin confirmar").lower()
    try:
        fecha = datetime.strptime(fecha_str, "%d/%m/%y")
    except:
        await ctx.send("❌ Fecha inválida. Usa formato dd/mm/aa")
        return
    lives.append({
        "nombre": nombre,
        "fecha": fecha.strftime("%d/%m/%y"),
        "confirmado": confirmado,
        "estado": "pendiente"
    })
    guardar_lives(lives)
    await ctx.send(f"✅ Live `{nombre}` creado para {fecha_str} ({confirmado})")

@bot.command()
@commands.has_permissions(administrator=True)
async def start_live(ctx, *, nombre: str):
    live = None
    for l in lives:
        if l["nombre"].lower() == nombre.lower():
            live = l
            break
    if not live:
        await ctx.send(f"❌ No se encontró el live `{nombre}`")
        return
    live["estado"] = "en vivo"
    guardar_lives(lives)
    await ctx.send(f"🔴 El live `{nombre}` ha comenzado!")

@bot.command()
async def lives(ctx):
    ahora = datetime.now()
    en_vivo = []
    proximos = []
    for l in lives:
        fecha = datetime.strptime(l["fecha"], "%d/%m/%y")
        if l["estado"] == "en vivo":
            en_vivo.append(l)
        elif fecha >= ahora:
            proximos.append(l)
    mensaje = "**🎥 Lives:**\n"
    if en_vivo:
        for l in en_vivo:
            mensaje += f"🔴 {l['nombre']} - En vivo\n"
    else:
        mensaje += "🔴 Ninguno en vivo\n"
    if proximos:
        for l in proximos:
            mensaje += f"📅 {l['nombre']} - {l['fecha']} ({l['confirmado']})\n"
    else:
        mensaje += "📅 No hay próximos lives\n"
    await ctx.send(mensaje)




@bot.command()
async def plantilla(ctx):
    user = ctx.author
    canal_destino_id = 1415360688599203870 # 🔹 Cambia por el ID real de #fichas-oc

    def check(m):
        return m.author == user and m.channel == ctx.channel

    try:
        # Preguntas paso a paso
        preguntas = [
            ("✍️ **Nombre del OC?**", "nombre"),
            ("🌀 **Clan del OC?**", "clan"),
            ("🏙️ **Aldea del OC?**", "aldea"),
            ("🌪️ **Elemento(s) del OC?**", "elementos"),
            ("🎯 **Aspiración del OC?**", "aspiracion"),
            ("👤 **Tu nombre en Roblox?**", "roblox"),
            ("📅 **Fecha de creación del OC?**", "fecha"),
        ]

        respuestas = {}

        for pregunta, key in preguntas:
            embed = discord.Embed(
                title="📋 Plantilla de OC",
                description=pregunta,
                color=discord.Color.blurple()
            )
            await ctx.send(embed=embed)
            msg = await bot.wait_for("message", check=check, timeout=90)
            respuestas[key] = msg.content

        # Pregunta de imagen obligatoria
        embed_img = discord.Embed(
            title="📋 Plantilla de OC",
            description="🖼️ **Manda una foto de tu OC (obligatoria)**",
            color=discord.Color.blurple()
        )
        await ctx.send(embed=embed_img)

        def check_img(m):
            return (
                m.author == user
                and m.channel == ctx.channel
                and (m.attachments or m.content.startswith("http"))
            )

        imagen_msg = await bot.wait_for("message", check=check_img, timeout=90)

        if not imagen_msg.attachments and not imagen_msg.content.startswith("http"):
            await ctx.send("❌ Debes mandar una imagen o un link de imagen válido. Plantilla cancelada.")
            return

        imagen_url = imagen_msg.attachments[0].url if imagen_msg.attachments else imagen_msg.content

        # Canal destino
        canal_destino = bot.get_channel(canal_destino_id)
        if not canal_destino:
            await ctx.send("⚠️ No encontré el canal destino, revisa el ID.")
            return

        # Texto con el formato que pediste
        ficha_texto = (
            "╔════════════════════════════╗\n"
            "       🌸 FICHA DE OC - ROLEPLAY 🌸\n"
            "╚════════════════════════════╝\n\n"
            f"🎴 **Nombre del OC:** {respuestas['nombre']}\n\n"
            f"👪 **Clan:** {respuestas['clan']}\n\n"
            f"🏙️ **Aldea:** {respuestas['aldea']}\n\n"
            f"🌪️ **Elemento(s):** {respuestas['elementos']}\n\n"
            f"🎯 **Aspiración:** {respuestas['aspiracion']}\n\n"
            f"👤 **Nombre en Roblox:** {respuestas['roblox']}\n\n"
            f"📅 **Fecha de creación:** {respuestas['fecha']}\n\n"
            f"🖼️ **Foto del OC:**\n{imagen_url}"
        )

        # Mandar ficha al canal fichas-oc
        await canal_destino.send(f"✅ Nueva ficha enviada por {user.mention}\n\n{ficha_texto}")

        # Confirmación en el canal original
        await ctx.send("📨 Tu ficha fue enviada correctamente a **#fichas-oc** ✅")

    except TimeoutError:
        await ctx.send(f"⏳ {user.mention}, tardaste demasiado en responder.")



# ----- INICIAR BOT -----
bot.run(os.getenv("DISCORD_TOKEN"))





