# bot.py
import os

import discord
from dotenv import load_dotenv

from discord.ext import commands

from difflib import SequenceMatcher

def similar(a, b):
    return (SequenceMatcher(None, a, b).ratio() > 0.4)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
BUZZ = int(os.getenv('DISCORD_BUZZ_ID'))

client = commands.Bot(command_prefix='!')

print(BUZZ)

tu_count = 1

tossup = False

buzz_channel = None

@client.command(name='packet', help="Tell Quizbot a packet is about to be played, so it can listen for buzzes.")
async def packet(ctx):
    global tossup
    global buzz_channel
    await buzz_channel.send("Let's quiz! Moderator, type !tu between each tossup and I'll handle buzzes.")
    global tu_count
    tu_count = 0

@client.command(name='tu', help="Signal the next tossup")
async def tossup(ctx):
    global buzz_channel
    global tu_count
    global tossup
    await buzz_channel.send("Tossup " + str(tu_count))
    tu_count += 1
    tossup = True

@client.event
async def on_ready():
    global buzz_channel
    print(f'{client.user.name} has connected to Discord!')
    buzz_channel = client.get_channel(BUZZ)

    print(buzz_channel)

@client.event
async def on_message(message):
    global tossup
    if (message.channel.id == BUZZ) and tossup:
        if client.user.id != message.author.id:
            if similar('buzz', message.content):
                await buzz_channel.send(str(message.author.name) + ' buzzed in first! Gwan, my son!')
                tossup = False
            else:
                await buzz_channel.send('Possible banter detected. Moderator discretion required.')
                tossup = False

    await client.process_commands(message)

client.run(TOKEN)
