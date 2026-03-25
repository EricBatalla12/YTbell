import discord
import feedparser
import requests
import os
import re
import json
from dotenv import load_dotenv
from discord.ext import commands, tasks

load_dotenv()

# ==========================================
# CONSTANTES Y MEMORIA
# ==========================================
SERVER_LIST = "servers.json"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ==========================================
# FUNCIONES
# ==========================================
def parse_channel_id(url):
    if not url.startswith(("http://", "https://")) or not ("youtube.com" in url or "youtu.be" in url):
        return "INVALID_URL"

    # If url has the channel_id, direct match
    direect_match = re.search(r"(UC[\w-]+)", url)
    if direect_match:
        return direect_match.group(1)
    
    patron = r"channel_id=(UC[\w-]+)" #Expresión regular

    respuesta = requests.get(url, timeout = 10)
    codigo_html = respuesta.text
    channel_id = re.search(patron, codigo_html)
    
    if channel_id:
        return channel_id.group(1)
    else:
        return None

#Function that load an entire json archive where are saved x servers
def data_loader():
    if os.path.exists(SERVER_LIST):
        with open(SERVER_LIST, "r") as archive:
            return json.load(archive)
    else:
        return {}

def data_saver(data):
    with open(SERVER_LIST, "w") as archive: # "w" erase the entire archive
        json.dump(data, archive, indent = 4)

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
    if not yt_watcher.is_running():
        yt_watcher.start()

@tasks.loop(minutes=10)
async def yt_watcher():
    
    data = data_loader()
    for guild_id in data:
        dst_channel_id = data[guild_id].get("dst_channel_id")
        rss = data[guild_id].get("rss")
        last_link_know = data[guild_id].get("last_link_know")
        if dst_channel_id is None or rss is None:
            continue #Next guild_id
        #Diccionario clave-valor     
        feed = feedparser.parse(rss)
        #feed.entries devuelve los últimos 15 videos más recientes
        if feed and len(feed.entries) > 0:
            for video in feed.entries:
                video_id = video.yt_videoid
                
                if not es_short(video_id):
                    actuall_link = video.link
                    actuall_title = video.title
                    
                    if last_link_know is None:
                        last_link_know = actuall_link
                        data[guild_id]["last_link_know"] = last_link_know
                        data_saver(data)
                        print(f"Sistema inicializado. Último VÍDEO en memoria: {actuall_title}")
                        
                    elif actuall_link != last_link_know:
                        channel_sender = bot.get_channel(dst_channel_id)
                        if channel_sender:
                            try:
                                await channel_sender.send(f"¡NUEVO VÍDEO DETECTADO!\n**{actuall_title}**\n{actuall_link}", silent=True)
                            except Exception as e:
                                print(f"Error al enviar el mensaje: {e}")
                                
                        last_link_know = actuall_link
                        data[guild_id]["last_link_know"] = last_link_know
                        data_saver(data)
                    else:
                        print("Chequeo rutinario: No hay vídeos nuevos.")
                    
                    break 

    

# ==========================================
# COMANDOS MANUALES
# ==========================================

@bot.command()
async def lv(ctx):
    data = data_loader()
    guild_id = str(ctx.guild.id)
    
    if guild_id not in data or data[guild_id].get("rss") is None:
        await ctx.send("Use `!setytchannel <url>` first.", silent=True)
        return

    rss = data[guild_id].get("rss")

    await ctx.send("Searching the lastest video...", silent=True)
    feed = feedparser.parse(rss)
    
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
    
    guild_id = str(ctx.guild.id)

    await ctx.send("Searching...", silent=True)
    yt_id = parse_channel_id(url_canal)
    
    if yt_id == "INVALID_URL":
        await ctx.send("❌Invalid url❌", silent = True)
        return
    
    if yt_id is None:
        await ctx.send("❌ I couldn't find the ID for that YT channel. Please make sure you provide a valid link.", silent=True)
        return

    data = data_loader()

    if guild_id not in data:
        data[guild_id] = {}

    rss = f"https://www.youtube.com/feeds/videos.xml?channel_id={yt_id}"

    if data[guild_id].get("rss") == rss:
        await ctx.send("This YT channel is already configurated to send notifications", silent = True) 
        return

    data[guild_id]["rss"] = rss
    data_saver(data)
    await ctx.send(f"✅ YT channel linked succefully", silent=True)
    print(f"New URL RSS: {rss}")

@setytchannel.error
async def setytchannel_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Necesitas permisos de Administrador para usar este comando.", silent=True)

@bot.command()
@commands.has_permissions(administrator=True)
async def setcanal(ctx):
    guild_id = str(ctx.guild.id)
    channel_id = ctx.channel.id

    data = data_loader()

    if guild_id not in data: #First time using bot in this guild
        data[guild_id] = {} 
    
    if data[guild_id].get("dst_channel_id") == channel_id: #This channel is already configured
        await ctx.send(f"{ctx.channel.mention} is already configured")
        return

    data[guild_id]["dst_channel_id"] = channel_id #RAM memory
    data_saver(data) #Really saved
    await ctx.send(f"{ctx.channel.mention} is ready to recieve notifications ✅", silent = True)

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