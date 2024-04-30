#bot.py file
import os

import discord
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
        
    on_ready()
        
@client.command()
async def test(ctx, arg):
    await ctx.send(arg)

@client.command()
async def add_role(user: discord.Member, role : discord.Role = 1233094863533379736):
    '''Adds the default role for a new server member'''
    
    if role in user.roles:
        return
    else: await user.add_roles(role)
    
        
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
    api_key = 'JOIbHCfh7HUOEelNPQO9jYCO9hM9RRFT'
    api_instance = giphy_client.DefaultApi()
    
    try:
            api_responce = api_instance.gifs_search_get(api_key, q, limit=100, rating='g')
            lst = list(api_responce.data)
            giff = random.choice(lst)
            print(giff)
            embed = discord.Embed(title = q)
            embed.set_image(url=f"https://media.giphy.com/media/{giff.id}/giphy.gif")
            
            await ctx.channel.send(embed=embed)
            print("If you're seeing this and the command hasn't properly executed then you've run out of API calls.")
    
    except ApiException as e:
        print(f"Exception from the API as: {e}")
        
    finally:
        print("If you didn't get the gif and the ApiException error wasn't thrown then, look here.")
        

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    msg = message.content.lower()
    
    words_list = ['gm', "good morning"]
    
    if any(word in msg for word in words_list):
        await message.channel.send(f"Good morning {message.author}!")
     
client.run(TOKEN)

