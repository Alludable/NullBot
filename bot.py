#bot.py file
import os

import discord
import yt_dlp
import requests, json
from dotenv import load_dotenv
from discord.ext import commands
import giphy_client
from giphy_client.rest import ApiException
import asyncio
import time
import random


intents = discord.Intents.all()
intents.message_content = True

client  = commands.Bot(command_prefix = "$", intents=intents)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SERVER = os.getenv('DISCORD_SERVER')
API_KEY = os.getenv('API_KEY')

ytdl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
            }],
        }
        
ytdl = yt_dlp.YoutubeDL(ytdl_opts)
ffmpeg_options = {'options': '-vn'}

def greeting():
    file = open('bot_greetings.txt', 'r')
    f_content = file.readlines()
    count = 0
    
    for line in f_content:
        count += 1
        
    line = (random.randint(0, (count - 1)))
    return f_content[line]

def farewell():
    file = open('bot_farewells.txt', 'r')
    f_content = file.readlines()
    count = 0
    
    for line in f_content:
        count += 1
        
    line = (random.randint(0, (count - 1)))
    return f_content[line]

@client.command(name = "hi")
async def SendMessage(ctx):
    await ctx.send("Hello!")

@client.event
async def on_ready():
    for server in client.guilds:
        if server.name == SERVER:
            break
    
    print(f'{client.user} is connected to the following server:\n'
          f'{server.name}(id: {server.id})')
    
    members = '\n - '.join([member.name for member in server.members])
    print(f'Server Members:\n - {members}')

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
            api_responce = api_instance.gifs_search_get(api_key, q, limit=100, rating='g')
            lst = list(api_responce.data)
            giff = random.choice(lst)
  
            embed = discord.Embed(title = q)
            embed.set_image(url=f"https://media.giphy.com/media/{giff.id}/giphy.gif")
            
            await ctx.channel.send(embed=embed)
            print("If you're seeing this and the command hasn't properly executed then you've run out of API calls.")
    
    except ApiException as e:
        print(f"Exception from the API as: {e}")
        
        

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
async def play(ctx, url : str=r'https://www.youtube.com/watch?v=dQw4w9WgXcQ'):
    try:
       if url == r'https://www.youtube.com/watch?v=dQw4w9WgXcQ':
           await ctx.channel.send("You didn't specify a url so I've chosen one for you. Enjoy :)") 
       else:
            voice_client = await ctx.author.voice.channel.connect()
            voice_clients = [voice_client.guild.id]
            voice_channel = discord.utils.get(ctx.guild.voice_channels, name="music-channel")

            await ctx.channel.send(f"```{client.user} has connected to music-channel.```")
            print(f"{client.user} has connected to {str(voice_channel)}.")
    
    except Exception as e:
        print(e)
        
    try:
        if url != r'https://www.youtube.com/watch?v=dQw4w9WgXcQ':
            url = ctx.message.content.split()[1]
        else:
            url = url
        
        loop =  asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        
        song = data['url']
        player = discord.FFmpegPCMAudio(song, **ffmpeg_options)
        
        voice_clients[ctx.message.guild.id].play(player)
    
    except Exception as e:
        print(e)
        
        
    
@client.command()
async def leave(ctx):
    voice_channel = discord.utils.get(ctx.guild.voice_channels, name="music-channel")
    voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
    if voice != None:
        if voice.is_connected():
            await voice.disconnect()
            print(f"{client.user} has disconnected from {str(voice_channel)}")
    else:
        await ctx.send("```I'm not currently connected to a voice channel.```")
        
@client.command()
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
    if not ctx.voice.channel:
        await ctx.channel.send("```I'm not currently in a voice channel.")
        return
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("```I'm not currently playing any audio.```")

@client.command
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
    if not ctx.voice.channel:
        await ctx.channel.send("```I'm not currently in a voice channel.```")
        return
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("```The audio hasn't been paused.```")
        
@client.command
async def stop(ctx):
    vc = ctx.VoiceClient.source
    voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
    if not ctx.voice.channel:
        await ctx.channel.send("```I'm not currently in a voice channel.```")
        return
    else:
        voice.stop()
    
            
client.run(TOKEN)