#v6
# Editamos $sorteo para unificarlo
import discord
import re
import random
from discord.ext import commands

# Habilita todos los intents para tener acceso completo a la información del servidor
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="$", intents=intents)

# Diccionario para almacenar los mensajes de sorteo por canal
sorteo_messages = {}

# Esta función encuentra el número más cercano a un número dado en una lista de números
def encontrar_numero_mas_cercano(numero, lista):
    return min(lista, key=lambda x: abs(numero - x))

# Función para crear un embed con el contenido dado
def crear_embed(titulo, descripcion, color):
    embed = discord.Embed(title=titulo, description=descripcion, color=color)
    return embed

# Comando de ayuda
@bot.hybrid_command(name="ayuda", description="Obtén una lista de los comandos disponibles")
async def ayuda(ctx: commands.Context):
       # Lista de comandos y descripciones
    commands_list = [
        {"name": "$sorteo (cantidad)", "description": "Inicia un sorteo de la cantidad especificada."},
        {"name": "$ganador", "description": "Selecciona un ganador del sorteo más reciente."},
        {"name": "$reroll", "description": "Selecciona un nuevo ganador del sorteo más reciente."},
        {"name": "$idganadora", "description": "Selecciona un ganador de un mensaje específico de sorteo."},
        {"name": "$cercano (cantidad)", "description": "Encuentra el número más cercano a un número dado en los mensajes del canal."},
        {"name": "$imprime", "description": "Guarda el historial de mensajes del canal en un archivo de texto y HTML."}
    ]

    # Construir el contenido del embed
    embed_description = "\n".join([f"- {cmd['name']}: {cmd['description']}" for cmd in commands_list])

    # Crear el embed
    embed = discord.Embed(title="Lista de Comandos", description=embed_description, color=0xFF7B00)

    # Enviar el embed
    await ctx.send(embed=embed)

# Evento que se activa cuando el bot se ha cargado y está listo para recibir comandos
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    # Sincronizamos con el servidor después de que el bot está listo
    await bot.tree.sync()
    # Imprimimos un mensaje para demostrar que nos hemos sincronizado correctamente
    print("Synchronized with the server")

# Evento que se activa cuando se envía un mensaje en el servidor
@bot.event
async def on_message(message):
    global sorteo_messages

    # Verificar si el autor del mensaje tiene permisos de administrador
    if not message.author.guild_permissions.administrator:
        return

    # Ignorar los mensajes del bot
    if message.author == bot.user:
        return

    # Comando para iniciar un sorteo con una cantidad específica
    elif message.content.startswith('$sorteo'):
        # Extraer la cantidad del mensaje
        try:
            cantidad = int(message.content.split()[1])
        except (IndexError, ValueError):
            await message.channel.send("Por favor, proporciona una cantidad válida después de $sorteo.")
            return

        # Verificar si la cantidad es válida
        if cantidad <= 0:
            await message.channel.send("La cantidad debe ser un número positivo.")
            return

        channel_id = message.channel.id
        if channel_id not in sorteo_messages:
            sorteo_messages[channel_id] = []

        embed = crear_embed(f"Sorteo de ${cantidad}", "Pulsa el emoji 🎉 para participar!", 0xFF7B00)
        sorteo_message = await message.channel.send(embed=embed)
        await sorteo_message.add_reaction('🎉')
        sorteo_messages[channel_id].append(sorteo_message.id)
        await message.delete()


    # Comando para seleccionar un ganador del sorteo
    elif message.content.startswith('$ganador'):
        channel_id = message.channel.id
        if channel_id not in sorteo_messages or not sorteo_messages[channel_id]:
            await message.channel.send("No hay ningún sorteo activo en este canal.")
            return

        sorteo_message_id = sorteo_messages[channel_id][-1]
        sorteo_message = await message.channel.fetch_message(sorteo_message_id)
        reacciones = sorteo_message.reactions

        if len(reacciones) == 0:
            await message.channel.send("Nadie ha participado en el sorteo.")
            return

        participantes = []
        async for user in reacciones[0].users():
            if user != bot.user:
                participantes.append(user)

        if len(participantes) == 0:
            await message.channel.send("Nadie ha participado en el sorteo.")
            return

        ganador = random.choice(participantes)
        embed = crear_embed("Ganador del Sorteo", f"¡El ganador del sorteo es: {ganador}/{ganador.mention}!", 0xFF7B00)
        await message.channel.send(embed=embed)
        await message.delete()

    # Comando para seleccionar un nuevo ganador del sorteo
    elif message.content.startswith('$reroll'):
        channel_id = message.channel.id
        if channel_id not in sorteo_messages or not sorteo_messages[channel_id]:
            await message.channel.send("No hay ningún sorteo activo en este canal.")
            return

        sorteo_message_id = sorteo_messages[channel_id][-1]
        sorteo_message = await message.channel.fetch_message(sorteo_message_id)
        reacciones = sorteo_message.reactions

        if len(reacciones) == 0:
            await message.channel.send("Nadie ha participado en el sorteo.")
            return

        participantes = []
        async for user in reacciones[0].users():
            if user != bot.user:
                participantes.append(user)

        if len(participantes) == 0:
            await message.channel.send("Nadie ha participado en el sorteo.")
            return

        nuevo_ganador = random.choice(participantes)
        embed = crear_embed("Nuevo Ganador del Sorteo", f"¡El nuevo ganador del sorteo es: {ganador}/{ganador.mention}!!", 0xFF7B00)
        await message.channel.send(embed=embed)
        await message.delete()

    # Comando para guardar el historial de mensajes del canal en un archivo de texto y HTML
    elif message.content.startswith('$imprime'):
        messages = []
        async for msg in message.channel.history(limit=None):
            messages.append(f"{msg.author.name}: {msg.content}")

        if messages:
            with open('chat_log.txt', 'w', encoding='utf-8') as file:
                for msg in messages:
                    file.write(f"{msg}\n")

            with open('chat_log.html', 'w', encoding='utf-8') as file:
                file.write('<html><head><title>Chat Log</title></head><body>')
                for msg in messages:
                    file.write(f"<p>{msg}</p>")
                file.write('</body></html>')

            await message.channel.send("Se ha generado el archivo de registro del chat.")
        else:
            await message.channel.send("No hay mensajes en el historial de este canal.")
        await message.delete()

    # Comando para encontrar el número más cercano a un número dado en los mensajes del canal
    elif message.content.startswith('$cercano'):
        try:
            numero_dado = float(message.content.split()[1])
        except (IndexError, ValueError):
            await message.channel.send("Por favor, proporciona un número válido después de $cercano.")
            return

        numeros_mensajes = []
        async for msg in message.channel.history(limit=None):
            # Ignorar mensajes del bot y mensajes que empiecen con $cercano
            if msg.author != bot.user and not msg.content.startswith('$cercano'):
                numeros = [float(numero) for numero in re.findall(r'\b\d+(?:\.\d+)?\b', msg.content)]
                if numeros:
                    numero_mas_cercano = encontrar_numero_mas_cercano(numero_dado, numeros)
                    numeros_mensajes.append((msg.author.name, msg.author.display_name, msg.content, numero_mas_cercano))

        if numeros_mensajes:
            usuario_nombre, usuario, mensaje, numero_mas_cercano = min(numeros_mensajes, key=lambda x: abs(numero_dado - x[3]))
            usuario = message.guild.get_member_named(usuario)

            if usuario:
                await message.channel.send(f"El número más próximo a {numero_dado} es el {numero_mas_cercano}, enviado por {usuario}/{usuario.mention}: '{mensaje}'")
            else:
                await message.channel.send(f"El número más próximo a {numero_dado} es el {numero_mas_cercano}, enviado por {usuario_nombre}: '{mensaje}'")
        else:
            await message.channel.send("No se encontraron números en los mensajes del chat.")
        await message.delete()


    # Comando para seleccionar un ganador de un mensaje específico de sorteo
    elif message.content.startswith('$idganadora'):
    # Obtener el ID del mensaje de sorteo desde el comando
        try:
            mensaje_id = int(message.content.split()[1])
        except (IndexError, ValueError):
            await message.channel.send("Por favor, proporciona un ID de mensaje válido después de $idganadora.")
            return

        # Obtener el mensaje de sorteo
        try:
            sorteo_message = await message.channel.fetch_message(mensaje_id)
        except discord.NotFound:
            await message.channel.send("No se encontró ningún mensaje con el ID proporcionado.")
            return

        # Verificar si el mensaje es un mensaje de sorteo
        if '🎉' not in [react.emoji for react in sorteo_message.reactions]:
            await message.channel.send("El mensaje proporcionado no es un mensaje de sorteo válido.")
            return

        # Obtener los participantes del mensaje de sorteo
        participantes = []
        async for user in sorteo_message.reactions[0].users():
            if user != bot.user:
                participantes.append(user)

        if len(participantes) == 0:
            await message.channel.send("Nadie ha participado en el sorteo.")
            return

        ganador = random.choice(participantes)
        embed = crear_embed("Ganador del Sorteo", f"¡El ganador del sorteo es: {ganador}/{ganador.mention}!", 0xFF7B00)
        await message.channel.send(embed=embed)
        await message.delete()

# Token de autenticación para el bot
bot.run("TOKEN")