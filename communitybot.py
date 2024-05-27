import discord
import json
import time
from discord.ext import commands
from discord.ext.commands import Greedy
from discord import User
from threading import Thread

#open text file in read mode
text_file = open("../bottoken.txt", "r")
#read whole file to a string
bottoken = text_file.read()
#close file
text_file.close()
# INTENTS
intents = discord.Intents(messages = True, guilds = True, reactions = True, members = True, presences = True)
bot = commands.Bot(command_prefix = '-', intents = intents)
bot.remove_command('help')

# load server output ch configs
guilddict = {}
jsonfile = '../guilds.txt'

try:
    with open(jsonfile, 'r') as fp:
        guilddict = json.load(fp)
except json.JSONDecodeError: pass

bot.guilddict = guilddict

# bot startup
@bot.event
async def on_ready(): 
    await bot.change_presence(activity=discord.Game(name="-help"))
    background_thread = Thread(target=write)
    background_thread.start()
    print('Bot is ready.')

# background task to write server contents to file every 15 mins
def write():
    while True:
        time.sleep(900)
        global guilddict
        with open(jsonfile, 'w') as fp:
            json.dump(guilddict, fp)
        fp.close()

cogs = ['cogs.help', 'cogs.reactions', 'cogs.serversettings', 'cogs.zakum']
for cog in cogs:
    bot.load_extension(cog)
    
bot.run(bottoken)