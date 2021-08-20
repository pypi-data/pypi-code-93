#!/usr/bin/env python3

import discord #To make a discord file
from os import write #To write to sample.png
import aiohttp#For async requests


baseurl = 'https://frenchnoodles.xyz/api/endpoints/'
#At some point, headers, aka authentication, will come back. When it does, I'll update the code here.

async def writeFile(res, session):
    file = open("sample.png", "wb")
    res = await res.read()
    file.write(res)
    file.close
    await session.close()

async def worthless(link):
    async with aiohttp.ClientSession() as session:
        params = {'link': f'{link}'}
        async with session.get(f'{baseurl}worthless?image={link}',
                            params=params) as res:
            try:
                response = await res.json()
                limit = response['You have passed your default quota!']
                return f'You have passed your default quota of {limit}.'
            except:
                await writeFile(res, session)
                return discord.File(fp="sample.png",filename="picture.png")

async def drake(link):
    async with aiohttp.ClientSession() as session:
        params = {'link': f'{link}'}
        async with session.get(f'{baseurl}drake?image={link}',
                            params=params) as res:
            try:
                response = await res.json()
                limit = response['You have passed your default quota!']
                return f'You have passed your default quota of {limit}.'
            except:
                await writeFile(res, session)
                return discord.File(fp="sample.png",filename="picture.png")

async def presidential(link):
    async with aiohttp.ClientSession() as session:
        params = {'link': f'{link}'}
        async with session.get(f'{baseurl}presidentialalert?image={link}',
                            params=params) as res:
            try:
                response = await res.json()
                limit = response['You have passed your default quota!']
                return f'You have passed your default quota of {limit}.'
            except:
                await writeFile(res, session)
                return discord.File(fp="sample.png",filename="picture.png")

async def spongebobburn(link):
    async with aiohttp.ClientSession() as session:
        params = {'link': f'{link}'}
        async with session.get(f'{baseurl}spongebobburnpaper?image={link}',
                            params=params) as res:
            try:
                response = await res.json()
                limit = response['You have passed your default quota!']
                return f'You have passed your default quota of {limit}.'
            except:
                await writeFile(res, session)
                return discord.File(fp="sample.png",filename="picture.png")

async def lisa(link):
    async with aiohttp.ClientSession() as session:
        params = {'link': f'{link}'}
        async with session.get(f'{baseurl}lisastage?image={link}',
                            params=params) as res:
            try:
                response = await res.json()
                limit = response['You have passed your default quota!']
                return f'You have passed your default quota of {limit}.'
            except:
                await writeFile(res, session)
                return discord.File(fp="sample.png",filename="picture.png")

async def changemind(link):
    async with aiohttp.ClientSession() as session:
        params = {'link': f'{link}'}
        async with session.get(f'{baseurl}changemymind?image={link}',
                            params=params) as res:
            try:
                response = await res.json()
                limit = response['You have passed your default quota!']
                return f'You have passed your default quota of {limit}.'
            except:
                await writeFile(res, session)
                return discord.File(fp="sample.png",filename="picture.png")

async def awkwardmonkey(link):
    async with aiohttp.ClientSession() as session:
        params = {'link': f'{link}'}
        async with session.get(f'{baseurl}awkwardmonkey?image={link}',
                            params=params) as res:
            try:
                response = await res.json()
                limit = response['You have passed your default quota!']
                return f'You have passed your default quota of {limit}.'
            except:
                await writeFile(res, session)
                return discord.File(fp="sample.png",filename="picture.png")

async def blur(link):
    async with aiohttp.ClientSession() as session:
        params = {'link': f'{link}'}
        async with session.get(f'{baseurl}blur?image={link}',
                            params=params) as res:
            try:
                response = await res.json()
                limit = response['You have passed your default quota!']
                return f'You have passed your default quota of {limit}.'
            except:
                await writeFile(res, session)
                return discord.File(fp="sample.png",filename="picture.png")
 
async def invert(link):
    async with aiohttp.ClientSession() as session:
        params = {'link': f'{link}'}
        async with session.get(f'{baseurl}invert?image={link}',
                            params=params) as res:
            try:
                response = await res.json()
                limit = response['You have passed your default quota!']
                return f'You have passed your default quota of {limit}.'
            except:
                await writeFile(res, session)
                return discord.File(fp="sample.png",filename="picture.png")

async def edge(link):
    async with aiohttp.ClientSession() as session:
        params = {'link': f'{link}'}
        async with session.get(f'{baseurl}edge?image={link}',
                            params=params) as res:
            try:
                response = await res.json()
                limit = response['You have passed your default quota!']
                return f'You have passed your default quota of {limit}.'
            except:
                await writeFile(res, session)
                return discord.File(fp="sample.png",filename="picture.png")

async def circle(link):
    async with aiohttp.ClientSession() as session:
        params = {'link': f'{link}'}
        async with session.get(f'{baseurl}circle?image={link}',
                            params=params) as res:
            try:
                response = await res.json()
                limit = response['You have passed your default quota!']
                return f'You have passed your default quota of {limit}.'
            except:
                await writeFile(res, session)
                return discord.File(fp="sample.png",filename="picture.png")

async def wide(link):
    async with aiohttp.ClientSession() as session:
        params = {'link': f'{link}'}
        async with session.get(f'{baseurl}wide?image={link}',
                            params=params) as res:
            try:
                response = await res.json()
                limit = response['You have passed your default quota!']
                return f'You have passed your default quota of {limit}.'
            except:
                await writeFile(res, session)
                return discord.File(fp="sample.png",filename="picture.png")

async def uglyupclose(link):
    async with aiohttp.ClientSession() as session:
        params = {'link': f'{link}'}
        async with session.get(f'{baseurl}uglyupclose?image={link}',
                            params=params) as res:
            try:
                response = await res.json()
                limit = response['You have passed your default quota!']
                return f'You have passed your default quota of {limit}.'
            except:
                await writeFile(res, session)
                return discord.File(fp="sample.png",filename="picture.png")

async def clown(link):
    async with aiohttp.ClientSession() as session:
        params = {'link': f'{link}'}
        async with session.get(f'{baseurl}clown?image={link}',
                            params=params) as res:
            try:
                response = await res.json()
                limit = response['You have passed your default quota!']
                return f'You have passed your default quota of {limit}.'
            except:
                await writeFile(res, session)
                return discord.File(fp="sample.png",filename="picture.png")

async def restpeace(link):
    async with aiohttp.ClientSession() as session:
        params = {'link': f'{link}'}
        async with session.get(f'{baseurl}rip?image={link}',
                            params=params) as res:
            try:
                response = await res.json()
                limit = response['You have passed your default quota!']
                return f'You have passed your default quota of {limit}.'
            except:
                await writeFile(res, session)
                return discord.File(fp="sample.png",filename="picture.png")

async def baby(link):
    async with aiohttp.ClientSession() as session:
        params = {'link': f'{link}'}
        async with session.get(f'{baseurl}affectbaby?image={link}',
                            params=params) as res:
            try:
                response = await res.json()
                limit = response['You have passed your default quota!']
                return f'You have passed your default quota of {limit}.'
            except:
                await writeFile(res, session)
                return discord.File(fp="sample.png",filename="picture.png")

async def trash(link):
    async with aiohttp.ClientSession() as session:
        params = {'link': f'{link}'}
        async with session.get(f'{baseurl}trash?image={link}',
                            params=params) as res:
            try:
                response = await res.json()
                limit = response['You have passed your default quota!']
                return f'You have passed your default quota of {limit}.'
            except:
                await writeFile(res, session)
                return discord.File(fp="sample.png",filename="picture.png")

async def welcomebanner(background, avatar, title, subtitle, textcolor):
    async with aiohttp.ClientSession() as session:
        params = {
   "background":"background",
   "avatar":"avatar",
   "title":"title",
   "subtitle":"subtitle",
   "textcolor":"textcolor"
}
        async with session.get(f'{baseurl}welcomebanner?background={background}&avatar={avatar}&title={title}&subtitle={subtitle}&textcolor={textcolor}',
        params=params) as res:
            try:
                response = await res.json()
                limit = response['You have passed your default quota!']
                return f'You have passed your default quota of {limit}.'
            except:
                await writeFile(res, session)
                return discord.File(fp="sample.png",filename="picture.png")

async def boostcard(link):
    async with aiohttp.ClientSession() as session:
        params = {'link': f'{link}'}
        async with session.get(f'{baseurl}boostercard?image={link}',
                            params=params) as res:
            try:
                response = await res.json()
                limit = response['You have passed your default quota!']
                return f'You have passed your default quota of {limit}.'
            except:
                await writeFile(res, session)
                return discord.File(fp="sample.png",filename="picture.png")

async def meme(link):
    async with aiohttp.ClientSession() as session:
        params = {'link': f'{link}'}
        async with session.get(f'{baseurl}randommeme',
                            params=params) as res:
            try:
                response = await res.json()
                limit = response['You have passed your default quota!']
                return f'You have passed your default quota of {limit}.'
            except:
                await writeFile(res, session)
                return discord.File(fp="sample.png",filename="picture.png")

async def balancecard(background, avatar, top, bottom, textcolor):
    async with aiohttp.ClientSession() as session:
        params = {
   "background":"background",
   "avatar":"avatar",
   "top":"top",
   "bottom":"bottom",
   "textcolor":"textcolor"
}
        async with session.get(f'{baseurl}balancecard?background={background}&avatar={avatar}&text1={top}&text2={bottom}&textcolor={textcolor}',
        params=params) as res:
            try:
                response = await res.json()
                limit = response['You have passed your default quota!']
                return f'You have passed your default quota of {limit}.'
            except:
                await writeFile(res, session)
                return discord.File(fp="sample.png",filename="picture.png")
