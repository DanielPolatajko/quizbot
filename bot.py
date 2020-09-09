# File to run Quizbot from external class in cogs.py
# Must provide discord tokens in .env file

import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from cogs import Quiz

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
BUZZ = int(os.getenv('DISCORD_BUZZ_ID'))

client = commands.Bot(command_prefix='!')

client.add_cog(Quiz(client, BUZZ))

client.run(TOKEN)
