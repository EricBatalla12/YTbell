import discord
import feedparser
import requests
import os
import re
from dotenv import load_dotenv
from discord.ext import commands, tasks

load_dotenv()

# ==========================================
# CONSTANTES Y MEMORIA (Se borran al apagar el bot)
# ==========================================
URL_RSS_GENERIC = None
canal_destino_id = None
ultimo_enlace_conocido = None


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ==========================================
# FUNCIONES
# ==========================================
def parse_channel_id(url):
    patron = r"channel_id=(UC[\w-]+)" #Expresión regular

    respuesta = requests.get(url, timeout = 10)
    codigo_html = respuesta.text
    channel_id = re.search(patron, codigo_html)
    
    if channel_id:
        return channel_id.group(1)
    else:
        return None

def es_short(video_id):
    url_prueba = f"https://www.youtube.com/shorts/{video_id}"
    try:
        respuesta = requests.head(url_prueba, allow_redirects=False, timeout=5)
        return respuesta.status_code == 200
    except Exception as e:
        print(f"Error comprobando el Short: {e}")
        return False

# ==========================================
# EVENTOS Y TAREAS EN SEGUNDO PLANO
# ==========================================

@bot.event
async def on_ready():
    print(f'El bot: {bot.user} está en funcionamiento')
    if not vigilar_youtube.is_running():
        vigilar_youtube.start()

@tasks.loop(minutes=10)
async def vigilar_youtube():
    global ultimo_enlace_conocido 
    global URL_RSS_GENERIC
    global canal_destino_id
    
    # Si no nos han dado una URL o un canal de Discord, no hacemos nada y esperamos
    if URL_RSS_GENERIC is None or canal_destino_id is None:
        return
    #Diccionario clave-valor     
    feed = feedparser.parse(URL_RSS_GENERIC)
    #feed.entries devuelve los últimos 15 videos más recientes
    if feed and len(feed.entries) > 0:
        for video in feed.entries:
            video_id = video.yt_videoid
            
            if not es_short(video_id):
                link_actual = video.link
                titulo_actual = video.title
                
                if ultimo_enlace_conocido is None:
                    ultimo_enlace_conocido = link_actual
                    print(f"Sistema inicializado. Último VÍDEO en memoria: {titulo_actual}")
                    
                elif link_actual != ultimo_enlace_conocido:
                    canal_destino = bot.get_channel(canal_destino_id)
                    if canal_destino:
                        try:
                            await canal_destino.send(f"¡NUEVO VÍDEO DETECTADO!\n**{titulo_actual}**\n{link_actual}", silent=True)
                        except Exception as e:
                            print(f"Error al enviar el mensaje: {e}")
                            
                    ultimo_enlace_conocido = link_actual
                else:
                    print("Chequeo rutinario: No hay vídeos nuevos.")
                
                break 

# ==========================================
# COMANDOS MANUALES
# ==========================================

@bot.command()
async def generic(ctx):
    global URL_RSS_GENERIC
    
    if URL_RSS_GENERIC is None:
        await ctx.send("¡Aún no me has dicho qué canal vigilar! Usa `!setytchannel <url>` primero.", silent=True)
        return

    await ctx.send("Buscando el último vídeo...", silent=True)
    feed = feedparser.parse(URL_RSS_GENERIC)
    
    if feed and len(feed.entries) > 0:
        for video in feed.entries:
            if not es_short(video.yt_videoid):
                titulo = video.title
                link = video.link
                await ctx.send(f"**{titulo}**\n{link}", silent=True)
                return
                
        await ctx.send("Vaya, parece que solo he encontrado Shorts recientemente.", silent=True)
    else:
        await ctx.send("Error de conexión con la base de datos de YouTube.", silent=True) 

@bot.command()
@commands.has_permissions(administrator=True)
async def setytchannel(ctx, url_canal: str):
    global URL_RSS_GENERIC
    id_del_canal = parse_channel_id(url_canal)
    print(f"ID: {id_del_canal}")
    # El bot construye la URL completa automáticamente juntando la base y la ID que le des
    URL_RSS_GENERIC = f"https://www.youtube.com/feeds/videos.xml?channel_id={id_del_canal}"
    
    await ctx.send(f"✅ Canal enlazado. URL construida y guardada en memoria: {URL_RSS_GENERIC}")

@bot.command()
@commands.has_permissions(administrator=True)
async def setcanal(ctx):
    global canal_destino_id

    if canal_destino_id == ctx.channel.id:
        await ctx.send("Este canal ya está notificado")
        return

    # Guardamos el canal de Discord en la memoria global
    canal_destino_id = ctx.channel.id
    
    await ctx.send(f"✅ Las alertas de vídeos llegarán a {ctx.channel.mention}", silent=True)

@setcanal.error
async def setcanal_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Necesitas permisos de Administrador para usar este comando.", silent=True)

# ==========================================
# ARRANQUE DEL BOT
# ==========================================

TOKEN = os.getenv("DISCORD_TOKEN") 

if TOKEN is None:
    print("Error: No se ha encontrado el token en las variables de entorno.")
else:
    bot.run(TOKEN)