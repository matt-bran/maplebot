import discord
import json
from discord.ext import commands
from discord.ext.commands import Greedy
from discord import User

#open text file in read mode
text_file = open("../bottoken.txt", "r")
#read whole file to a string
bottoken = text_file.read()
#close file
text_file.close()
intents = discord.Intents(messages = True, guilds = True, reactions = True, members = True, presences = True)
bot = commands.Bot(command_prefix = '-', intents = intents)
# load guild info
guilddict = {}
jsonfile = '../guilds.txt'
try:
    with open(jsonfile, 'r') as fp:
        guilddict = json.load(fp)
except json.JSONDecodeError: pass

# bot startup
@bot.event
async def on_ready(): 
    await bot.change_presence(activity=discord.Game(name="-help"))
    print('Bot is ready.')

# Initialize the channel that the user wants the boss run
# sign up sheet sent to as well as initializing the channel that
# the command will be expected to be received from on the discord server
# to avoid the possibility of other users spamming the command.
@bot.command()
async def init(ctx, bossid):
    exists = False
    for channel in ctx.guild.text_channels:
        channelid = channel.id 
        if str(channelid) == bossid: exists = True
    if not exists: return
    guildID = str(ctx.guild.id)
    bot_chID = str(ctx.channel.id)
    boss_chID = str(bossid)
    guilddict[guildID] = (bot_chID, boss_chID)
    with open(jsonfile, 'w') as fp:
        json.dump(guilddict, fp)

# Takes two integers for desired * of attackers and bishops 
# followed by a "sentence in qoutes" as a description and creates
# a reaction based sign up sheet for Zakum boss runs. 
@bot.command()
async def zak(ctx, *args):
    guild = ctx.guild
    guildID = str(ctx.guild.id)
    try:
        bot_channel = guilddict[guildID][0]
        boss_channel = guilddict[guildID][1]
    except KeyError:
        await ctx.send(content="The bot and boss channel hasn't been initialized.")
        return
    if str(ctx.channel.id) != bot_channel: return
    att_lim = args[0]
    bsh_lim = args[1]
    desc = args[2]
    if not isDigit(att_lim) or not isDigit(bsh_lim): return
    embed = discord.Embed(title="Zakum Runs", description = desc)
    embed.set_thumbnail(url="https://static.wikia.nocookie.net/maplestory/images/f/f2/Monster_Zakum.png/revision/latest?cb=20140101121359&path-prefix=pl")
    embed.add_field(name = "Attackers: 0/{} ⚔️".format(att_lim), value='\u200b', inline = True)
    embed.add_field(name = "Bishops: 0/{} 🇨🇭".format(bsh_lim), value='\u200b', inline = True)
    embed.add_field(name = 'Helms 🪖', value='\u200b', inline = True)
    embed.set_author(name=ctx.author.display_name + " is hosting", icon_url=ctx.author.avatar_url)
    boss_role = discord.utils.get(guild.roles, name="Bossing")
    helm_role = discord.utils.get(guild.roles, name="Zakum Helmet")
    roles = [boss_role, helm_role]
    boss_channel = guild.get_channel(int(boss_channel))
    message = await boss_channel.send(content="".join(role.mention for role in roles),embed=embed)
    await message.add_reaction('⚔️')
    await message.add_reaction('🇨🇭')
    await message.add_reaction('🪖')

# adds a user to the list when they react
@bot.event
async def on_reaction_add(reaction, user):
    if user.bot: return
    embeds = reaction.message.embeds
    list = embeds[0].fields
    sec_list = ""
    sec_index = -1
    fname = ""
    if reaction.emoji == '⚔️':
        sec_index = 0
        replace_indx = 11
        fname = list[sec_index].name
        fname = fname[:replace_indx] + str(int(fname[replace_indx]) + 1) + fname[replace_indx + 1:]
    elif reaction.emoji == '🇨🇭':
        sec_index = 1
        replace_indx = 9
        fname = list[sec_index].name
        fname = fname[:replace_indx] + str(int(fname[replace_indx]) + 1) + fname[replace_indx + 1:]
    elif reaction.emoji == '🪖':
        sec_index = 2
        fname = list[sec_index].name
    else: return
    sec_list = list[sec_index].value
    sec_list = add(sec_list, user)
    embeds[0].set_field_at(sec_index, name = fname, value=sec_list)
    await reaction.message.edit(embed = embeds[0])

# handles removing a user from the list when they un-react
@bot.event
async def on_reaction_remove(reaction, user):
    if user.bot: return
    embeds = reaction.message.embeds
    list = embeds[0].fields
    sec_list = ""
    sec_index = -1
    fname = ""
    if reaction.emoji == '⚔️':
        sec_index = 0
        replace_indx = 11
        fname = list[sec_index].name
        fname = fname[:replace_indx] + str(int(fname[replace_indx]) - 1) + fname[replace_indx + 1:]
    elif reaction.emoji == '🇨🇭':
        sec_index = 1
        replace_indx = 9
        fname = list[sec_index].name
        fname = fname[:replace_indx] + str(int(fname[replace_indx]) - 1) + fname[replace_indx + 1:]
    elif reaction.emoji == '🪖':
        sec_index = 2
        fname = list[sec_index].name
    else: return  
    sec_list = list[sec_index].value
    sec_list = rem(sec_list, user)
    embeds[0].set_field_at(sec_index, name = fname, value=sec_list)
    await reaction.message.edit(embed = embeds[0])

# helper
def add(string, user):
    if string == '\u200b': string = user.display_name
    else: string += "\n" + user.display_name
    return string

# helper
def rem(string, user):
    string = string.replace(user.display_name, '') 
    if not string: string = '\u200b'
    return string

# helper
def isDigit(c):
    if (c>='0' and c<='9'): return True
    else: return False

bot.run(bottoken)