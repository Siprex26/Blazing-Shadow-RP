import discord
from discord.ext import commands, tasks
import os
from datetime import datetime, timedelta
import actividad
import json
import random
import requests


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
    canal_destino_id = 1415360688599203870  # Canal fijo #fichas-oc
    respuestas = {}

    # ---------- MENÚ DE CLAN ----------
    class ClanSelect(discord.ui.Select):
        def __init__(self, guild):
            opciones = []
            for clan, limite in clanes_limites.items():
                role = discord.utils.get(guild.roles, name=clan)
                miembros = len(role.members) if role else 0
                if miembros < limite:
                    opciones.append(discord.SelectOption(label=clan))

            if not opciones:
                opciones.append(discord.SelectOption(label="❌ Todos los clanes llenos", value="ninguno", default=True))

            super().__init__(
                placeholder="👪 Selecciona el clan de tu OC",
                min_values=1,
                max_values=1,
                options=opciones
            )

        async def callback(self, interaction: discord.Interaction):
            if interaction.user != user:
                await interaction.response.send_message("❌ No puedes responder esta plantilla.", ephemeral=True)
                return

            role = discord.utils.get(interaction.guild.roles, name=self.values[0])
            if role and len(role.members) >= clanes_limites.get(self.values[0], 0):
                await interaction.response.send_message(f"❌ El clan **{self.values[0]}** está lleno. Elige otro.", ephemeral=True)
                return

            respuestas["clan"] = self.values[0]
            await interaction.response.send_message(f"✅ Clan seleccionado: **{self.values[0]}**", ephemeral=True)
            self.view.stop()

    class ClanView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=90)
            self.add_item(ClanSelect(ctx.guild))

    view_clan = ClanView()
    await ctx.send("🌀 **Selecciona el clan de tu OC**", view=view_clan)
    await view_clan.wait()
    if "clan" not in respuestas:
        await ctx.send("❌ Debes seleccionar un clan. Plantilla cancelada.")
        return

    # ---------- MENÚ DE ALDEA ----------
    class AldeaSelect(discord.ui.Select):
        def __init__(self):
            opciones = []
            for a in aldeas_list:
                role = discord.utils.get(ctx.guild.roles, name=a)
                if not role or len(role.members) < LIMITE_ALDEAS:
                    opciones.append(discord.SelectOption(label=a))

            super().__init__(
                placeholder="🏙️ Selecciona la aldea de tu OC",
                min_values=1,
                max_values=1,
                options=opciones
            )

        async def callback(self, interaction: discord.Interaction):
            if interaction.user != user:
                await interaction.response.send_message("❌ No puedes responder esta plantilla.", ephemeral=True)
                return

            respuestas["aldea"] = self.values[0]
            await interaction.response.send_message(f"✅ Aldea seleccionada: **{self.values[0]}**", ephemeral=True)
            self.view.stop()

    class AldeaView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=90)
            self.add_item(AldeaSelect())

    view_aldea = AldeaView()
    await ctx.send("🏙️ **Selecciona la aldea de tu OC**", view=view_aldea)
    await view_aldea.wait()
    if "aldea" not in respuestas:
        await ctx.send("❌ Debes seleccionar una aldea. Plantilla cancelada.")
        return

  # ---------- MENÚ DE ELEMENTOS ----------

    class ElementoSelect(discord.ui.Select):
        def __init__(self):
            opciones = [
                discord.SelectOption(label="🔥 Fuego"),
                discord.SelectOption(label="⚡ Electricidad"),
                discord.SelectOption(label="🌍 Tierra"),
                discord.SelectOption(label="💧 Agua"),
                discord.SelectOption(label="🌪️ Aire"),
            ]
            super().__init__(
                placeholder="🌪️ Selecciona **2 elementos** de tu OC",
                min_values=2,
                max_values=2,  # ✅ Solo 2 permitidos
                options=opciones
            )

        async def callback(self, interaction: discord.Interaction):
            if interaction.user != user:
                await interaction.response.send_message(
                    "❌ No puedes responder esta plantilla.",
                    ephemeral=True
                )
                return
            respuestas["elementos"] = ", ".join(self.values)
            await interaction.response.send_message(
                f"✅ Elementos seleccionados: **{respuestas['elementos']}**",
                ephemeral=True
            )
            self.view.stop()

    class ElementoView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=90)
            self.add_item(ElementoSelect())

    # 🔹 Aquí ya está dentro de la función async
    view_elemento = ElementoView()
    await ctx.send("🌪️ **Selecciona los elementos de tu OC**", view=view_elemento)
    await view_elemento.wait()
    if "elementos" not in respuestas:
        await ctx.send("❌ Debes seleccionar al menos un elemento. Plantilla cancelada.")
        return

    # ---------- PREGUNTAS DE TEXTO ----------
    preguntas_texto = [
        ("✍️ **Nombre del OC?**", "nombre"),
        ("🎯 **Aspiración del OC?**", "aspiracion"),
        ("👤 **Tu nombre en Roblox?**", "roblox"),
    ]

    def check_msg(m):
        return m.author == user and m.channel == ctx.channel

    for pregunta, key in preguntas_texto:
        await ctx.send(pregunta)
        msg = await bot.wait_for("message", check=check_msg, timeout=90)
        respuestas[key] = msg.content

    # ---------- FECHA AUTOMÁTICA ----------
    respuestas["fecha"] = datetime.now().strftime("%d/%m/%Y")

    # ---------- PREGUNTA DE IMAGEN ----------
    await ctx.send("🖼️ **Manda una foto de tu OC (obligatoria)**")

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

    # ---------- ENVIAR FICHA ----------
    canal_destino = bot.get_channel(canal_destino_id)
    if not canal_destino:
        await ctx.send("⚠️ No encontré el canal destino, revisa el ID.")
        return

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

    await canal_destino.send(f"✅ Nueva ficha enviada por {user.mention}\n\n{ficha_texto}")
    await ctx.send("📨 Tu ficha fue enviada correctamente a **#fichas-oc** ✅")


import discord
from discord.ext import commands
import random
import requests

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# Configuración
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBfaWQiOiIxNDE2NjU2NTMyNzk1NDI4MTE5IiwiaWF0IjoxNzU3ODI3NjM3fQ.sNghL7XGFEOR8ypraNRRFGbTbV7JKsQy9Wv2-vuYcos"   # 👈 pon aquí tu API Key
GUILD_ID = "1408955335607062541"

def quitar_dinero(user_id, cantidad):
    url = f"https://unbelievaboat.com/api/v1/guilds/{GUILD_ID}/users/{user_id}"
    headers = {"Authorization": API_KEY, "Content-Type": "application/json"}
    data = {"cash": -cantidad}  # 👈 forma correcta
    r = requests.patch(url, headers=headers, json=data)
    return r.json()

@bot.command()
async def ruleta(ctx):
    user_id = str(ctx.author.id)

    # Intentamos cobrar 100,000
    resultado_api = quitar_dinero(user_id, 100000)

    # Si la API devuelve cash significa que la operación fue válida
    if "cash" in resultado_api:
        numero = random.randint(1, 100)
        resultado = "Nada"
        if numero == 1:
            resultado = "🔥 Ashura"
        elif numero == 2:
            resultado = "⚡ Indra"
        elif numero <= 4:
            resultado = "🧬 Células"

        embed = discord.Embed(
            title="🎰 Ruleta Ninja",
            description=f"Resultado: **{resultado}**",
            color=discord.Color.random()
        )
        embed.set_footer(text=f"Pedido por {ctx.author.display_name}")
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ No tienes suficiente dinero para girar la ruleta (100,000).")
    

# ----- INICIAR BOT -----
bot.run(os.getenv("DISCORD_TOKEN"))













