#bot.py file
import os

import discord
from pytube import YouTube
import urllib.parse, urllib.request, re
import yt_dlp
from dotenv import load_dotenv
from discord.ext import commands
import giphy_client
from giphy_client.rest import ApiException
import asyncio
import random


intents = discord.Intents.all()
intents.message_content = True
command_prefix = r'$'

client  = commands.Bot(command_prefix = command_prefix, intents=intents)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SERVER = os.getenv('DISCORD_SERVER')
API_KEY = os.getenv('API_KEY')

youtube_base_url = 'https://www.youtube.com/'
youtube_results_url = youtube_base_url + 'results?'
youtube_watch_url = youtube_base_url + 'watch?v='
queues = {}
music_state = {
    "repeat_songs": 0,
    "current_song": None
}
voice_clients = {}
ytdl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        
ytdl = yt_dlp.YoutubeDL(ytdl_opts)
ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

def greeting():
    file = open('bot_greetings.txt', 'r')
    f_content = file.readlines()
    count = 0
    
    for line in f_content:
        count += 1
        
    line = (random.randint(0, (count - 1)))
    file.close()
    return f_content[line]

def farewell():
    file = open('bot_farewells.txt', 'r')
    f_content = file.readlines()
    count = 0
    
    for line in f_content:
        count += 1
        
    line = (random.randint(0, (count - 1)))
    file.close()
    return f_content[line]

def grab_quote():
    file = open('quotes.txt', 'r')
    f_content = file.readlines()
    count = 0
    
    for line in f_content:
        count += 1
        
    line = (random.randint(0, (count - 1)))
    file.close()
    return f_content[line]

def getv_title(url: str):
    youtube = YouTube(url)
    return youtube.title

@client.command()
async def cmds(ctx):
    await ctx.message.author.send(f"```Hello {ctx.message.author.name}!\nI see that you're in need of some help so I've compiled a list of my commands and how to use them for you!\n\t-To play music type '{command_prefix}play [enter the url here (or if you prefer a random term and I'll look for the first result)].\n\t-To pause the music type '{command_prefix}pause'\n\t-To resume the music type '{command_prefix}resume'.\n\t-To have me leave the voice call type '{command_prefix}leave' while you're in the same voice channel.\n\t-To stop the music entirely type '{command_prefix}stop'.\n\t-To queue music type '{command_prefix}queue [enter the url here (or if you prefer a random term and I'll look for the first result)].\n\t-To skip a song type '{command_prefix}skip' (This only works if there's a queue).\n\tTo completely clear the queue type '{command_prefix}clear_queue'.\n\t-To display the current songs in the queue type '{command_prefix}display_queue'.\n\t-To have me generate a gif type '{command_prefix}gif (you can specify a search term here).\n\t-To kick someone type '{command_prefix}kick @user [enter reason]'.\n\t-To ban someone type '{command_prefix}ban @user [enter reason]'.\n\t-To simply warn someone type '{command_prefix}warn @user [enter reason]'.\n\t-To receive a random quote type '{command_prefix}quote.'\nThese are all of my current commands, be responsible!```")

@client.command(name = "hi")
async def SendMessage(ctx):
    await ctx.send("Hello!")
    
@client.command()
async def creator(ctx):
    await ctx.send("```I was built by Oluwaseun Adeyemo. I think he's working at Apple right now...```")
    
@client.command()
async def quote(ctx):
    quote = grab_quote()
    await ctx.send(f"```{quote}```")

@client.event
async def on_ready():
    for server in client.guilds:
        if server.name == SERVER:
            break
    
    print(f'{client.user} is connected to the following server:\n'
          f'{server.name}(id: {server.id})')
    
    members = '\n - '.join([member.name for member in server.members])
    print(f'Server Members:\n - {members}')
    await client.change_presence(activity=discord.Game("Type {command_prefix}cmds if you need help."))
    
@client.event
async def on_member_join(member):
    user_greeting = greeting()
    user_greeting = user_greeting.replace("{user}", member.global_name)
    welcome_channel = client.get_channel(1232388230079320205)
    try:
        embed = discord.Embed(
            title = user_greeting,
            description="We're glad to have you here!",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.avatar.url)
        await welcome_channel.send(embed=embed)
    except:
        print(f"Couldn't message {member.name}")
        embed = discord.Embed(
            title = user_greeting,
            description="We're glad to have you here!",
            color=discord.Color.green()
        )
        
    role = discord.utils.get(member.guild.roles, name='Followers')
    
    await member.add_roles(role)
    await welcome_channel.send(f"{member.mention}, you have been assinged the role of {role}.")    
    await on_ready()
        
@client.command()
async def test(ctx, args):
    await ctx.send(args)
    
@client.command()
@commands.has_permissions(administrator=True)
async def kick(ctx, member: discord.Member = None, *,reason="No reason"):
    await member.kick(reason = reason)
    await ctx.send(f"```Kicked {member.name} for '{reason}'```")
    await member.send(f"```You have been *Kicked* by *{ctx.author.name}* in {ctx.guild.name} for '{reason}'```.")
    
@client.command()
@commands.has_permissions(administrator=True)
async def ban(ctx, member: discord.Member = None, *,reason="No reason"):
    await member.ban(reason = reason)
    await ctx.send(f"```Banned {member.name}. '{reason}'```")    
    
@client.command()
@commands.has_permissions(administrator=True)
async def warn(ctx, member: discord.Member = None, *,reason="No reason"):
    await member.send(f"```You have been *Warned* by *{ctx.author.name}* in {ctx.guild.name} for '{reason}'```.")
    await ctx.send(f"```Warned {member.name}.```")
        
@client.event
async def on_member_remove(member):
    user_farewell = farewell()
    user_farewell = user_farewell.replace("{user}", member.global_name)
    welcome_channel = client.get_channel(1232388230079320205)
    print("Recognised that a member called " + member.name + " left")
    try:
        embed=discord.Embed(
        title="😢 Goodbye "+ member.global_name + "!",
        description=user_farewell,
        color=discord.Color.dark_red()
        )
        embed.set_thumbnail(url=member.avatar.url)
        await welcome_channel.send(embed=embed)
    except:
        print(f"Couldn't write departure message for {member.name}")
        embed=discord.Embed(
        title="😢 Goodbye "+member.name+"!",
        description="Until we meet again old friend.",
        color=discord.Color.dark_red()
        )
        
@client.command()
async def gif(ctx,*,q="One Piece"):
    api_key = API_KEY
    api_instance = giphy_client.DefaultApi()
    
    try:
            api_responce = api_instance.gifs_search_get(api_key, q, limit=100, rating='r')
            lst = list(api_responce.data)
            giff = random.choice(lst)
  
            embed = discord.Embed(title = q)
            embed.set_image(url=f"https://media.giphy.com/media/{giff.id}/giphy.gif")
            
            await ctx.channel.send(embed=embed)
        
    except ApiException as e:
        print(f"Exception from the API as: {e}")
        print("If you're seeing this and the command hasn't properly executed then you've run out of API calls.")
    
        
        
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    msg = message.content.lower()
    
    words_list = ['gm', "good morning"]
    if any(word in msg for word in words_list):
        await message.channel.send(f"Good morning {message.author}!")
        
    await client.process_commands(message)
    
@client.command()
async def play(ctx,*, url : str=r'https://www.youtube.com/watch?v=dQw4w9WgXcQ'):
    try:
       if url == r'https://www.youtube.com/watch?v=dQw4w9WgXcQ':
           await ctx.channel.send("You didn't specify a url so I've chosen one for you. Enjoy :)") 
       
       if ctx.author.voice == None:
           await ctx.send("```You must join a voice channel first.```")
           return
       
       voice_client = await ctx.author.voice.channel.connect()
       voice_clients[voice_client.guild.id] = voice_client
       voice_channel = discord.utils.get(ctx.guild.voice_channels, name="music-channel")
       
       await ctx.channel.send(f"```{client.user} has connected to music-channel.```")
       print(f"{client.user} has connected to {str(voice_channel)}.")
    
    except Exception as e:
        print(e)
        
    try:
        
        if "www.youtube.com" not in url:
            search_query = urllib.parse.urlencode({'search_query': url})
            
            content = urllib.request.urlopen(youtube_results_url + search_query)
            results = re.findall(r'\watch\?v=(.{11})', content.read().decode())
            
            url = youtube_watch_url + results[0]        
            
        loop =  asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        
        song = data['url']
        player = discord.FFmpegOpusAudio(song, **ffmpeg_options)
        video_title = getv_title(url)
        voice_clients[ctx.guild.id].play(player, after = lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), client.loop))
        await ctx.send(f"```Currently Playing: {video_title}```")
    
    except Exception as e:
        print(e)
        
@client.command(name='clear_queue')
async def clear_queue(ctx):
    if ctx.guild.id in queues:
        queues[ctx.message.guild.id].clear()
        await ctx.send("```The queue has been cleared.```")
    else:
        await ctx.send("```There is no queue to clear.```")
        
@client.command(name='skip')
async def skip(ctx):
   voice = ctx.message.guild.voice_client
   if not voice or not voice_clients[ctx.guild.id]:
        await ctx.send("```I'm not currently playing any audio.```")
   elif not queues:
       await ctx.send("```There's no queue.```")
   elif voice_clients[ctx.guild.id]:
       voice_clients[ctx.guild.id].stop()
       await ctx.send("```Skipped the current track.```")
       await play_next(ctx)
   
@client.command()
async def leave(ctx):
    voice_channel = discord.utils.get(ctx.guild.voice_channels, name="music-channel")
    voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
    if voice != None:
        if voice.is_connected():
            await voice.disconnect()
            del voice_clients[ctx.guild.id]
            print(f"{client.user} has disconnected from {str(voice_channel)}")
    else:
        await ctx.send("```I'm not currently connected to a voice channel.```")
        
@client.command()
async def pause(ctx):
    voice = ctx.message.guild.voice_client
    if not voice:
        await ctx.channel.send("```I'm not currently in a voice channel.```")
        return
    elif voice_clients[ctx.guild.id].is_playing():
        voice_clients[ctx.guild.id].pause()
        await ctx.channel.send("```The music was paused.```")   
    else:
        await ctx.send("```I'm not currently playing any audio.```")

@client.command()
async def resume(ctx):
    voice = ctx.message.guild.voice_client
    if not voice:
        await ctx.channel.send("```I'm not currently in a voice channel.```")
        return
    elif voice_clients[ctx.guild.id].is_paused():
        voice_clients[ctx.guild.id].resume()
        await ctx.channel.send("```The music was resumed.```")
    else:
        await ctx.send("```The audio hasn't been paused.```")
        
@client.command()
async def stop(ctx):
    voice = ctx.message.guild.voice_client
    if not voice:
        await ctx.channel.send("```I'm not currently in a voice channel.```")
        return
    elif voice_clients[ctx.guild.id].is_playing():
        voice_clients[ctx.guild.id].stop()
        await ctx.channel.send("```The music was stopped.```")
    else:
        await ctx.send("```I'm not currently playing any audio.```")
        
@client.command(name='queue')
async def queue(ctx,*,url):
    if ctx.guild.id not in queues:
        queues[ctx.guild.id] = []
    if "www.youtube.com" in url:
        video_title = getv_title(url)
    else:
        video_title = url
    queues[ctx.guild.id].append(url)
    await ctx.send(f"```Added '{video_title}' to the queue.```")
    
    
@client.command()
async def display_queue(ctx):
    if ctx.guild.id not in queues:
        await ctx.send("```There's currently no items in your queue.```")
        return
    output_string = '\n'.join(getv_title(str(value)) for value in queues[ctx.guild.id])
    if len(output_string) == 0:
        await ctx.send("```There's currently no items in your queue.```")
    else:
        await ctx.send(f"```Here's the current items in the queue: \n{output_string}```")
    
async def play_next(ctx):
    if queues[ctx.guild.id]:
        url = queues[ctx.guild.id].pop(0)
        await play(ctx, url=url)
        

client.run(TOKEN)
