import discord
import json
from discord.ext import commands
from discord.ext.commands import Greedy
from discord import User

# url for zak img
urlZak="https://static.wikia.nocookie.net/maplestory/images/f/f2/Monster_Zakum.png/revision/latest?cb=20140101121359&path-prefix=pl"
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
# DEFINE CONSTANTS
ATTACKERS, BISHOPS, LOOTERS = 'Attackers: ', 'Bishops: ', 'Buyers 🪖'

# load server output ch configs
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

@bot.command()
async def greet(ctx):
    global guilddict
    guilddict[str(ctx.guild.id)] = ['', '', True, [], '']
    write()

@bot.command()
async def help(ctx):
    help = []
    help.append('-add <party role> <name entry> | adds the name entry to the column corresponding to the specified party role. The options are attacker, bishop, buyer.')
    help.append('-remove <party role> <name entry> | removes the name entry to the column corresponding to the specified party role. The options are attacker, bishop, buyer.')
    help.append('-input | Sets the current channel message was sent from as channel to receive sign-up log messages.')
    help.append('-output <bossing channel id> | sets the channel to send the bossing sheet to.')
    help.append('-toggleMention | toggles prescence of mentions in the sign up sheet. On by defualt.')
    await(ctx.send(('```' + '\n'.join(help) + '```')))

# Initialize the channel that the user wants the boss run
# sign up sheet sent to from now on
@bot.command()
async def output(ctx, out_id):
    global guilddict
    exists = False
    for channel in ctx.guild.text_channels:
        ch_name = channel.name
        channelid = channel.id 
        if str(channelid) == out_id: 
            exists = True
            break
    if not exists: return
    guildID = str(ctx.guild.id)
    guilddict[guildID][0] = out_id
    await(ctx.send('Output has been set to: ' + ch_name))
    write()

# Initialize the channel that the user wants the boss run
# sign up sheet sent to from now on
@bot.command()
async def input(ctx):
    global guilddict
    guildID = str(ctx.guild.id)
    guilddict[guildID][1] = ctx.channel.id
    await(ctx.send('Input has been set. Logs will be sent to: {}'.format(ctx.channel.name)))
    write()

# Takes two integers for desired * of attackers and bishops 
# followed by a "sentence in qoutes" as a description and creates
# a reaction based sign up sheet for Zakum boss runs. 
@bot.command(pass_context=True)
async def zak(ctx, *, args):
    global guilddict
    guild = ctx.guild
    guildID = str(ctx.guild.id)
    try:
        out_id = guilddict[guildID][0]
    except KeyError:
        await ctx.send(content="The output channel hasn't been set. Use `-output channelID`. Right click the channel you want to send to and copy the id.")
        return
    att_lim, bish_lim, desc = args[0], args[2], args[3:]
    if not isDigit(att_lim) or not isDigit(bish_lim): return
    embed = makeEmbed("Zakum runs", urlZak, desc, ATTACKERS + "0/{} ⚔️".format(att_lim), 
                                                        BISHOPS + "0/{} 🇨🇭".format(bish_lim), LOOTERS)
    embed.set_author(name=ctx.author.display_name + " is hosting", icon_url=ctx.author.avatar_url)
    boss_role = discord.utils.get(guild.roles, name="Bossing")
    helm_role = discord.utils.get(guild.roles, name="Zakum Helmet")
    roles = [boss_role, helm_role]
    out_channel = guild.get_channel(int(out_id))
    if guilddict[guildID][2]: recentMsg = await out_channel.send(content="".join(role.mention for role in roles),embed=embed)
    else: recentMsg = await out_channel.send(embed=embed)
    await recentMsg.add_reaction('⚔️')
    await recentMsg.add_reaction('🇨🇭')
    att_list, bish_list, loot_list = [], [], []    
    sign_list = []
    sign_list.append(att_list)
    sign_list.append(bish_list)
    sign_list.append(loot_list)
    guilddict[guildID][3] = sign_list
    guilddict[guildID][4] = recentMsg.id
    write()

@bot.command(passContext=True)
async def add(ctx, *, args):
    global guilddict
    guildID = str(ctx.guild.id)
    sign_list = guilddict[guildID][3]
    args = args.split(" ", 1)
    category = args[0]
    name = args[1]
    channel = bot.get_channel(int(guilddict[guildID][0]))
    msg = await channel.fetch_message(guilddict[guildID][4])
    embeds = msg.embeds
    col_list = embeds[0].fields
    if category == 'attacker':
        index = 0
        sign_list[index].append(name)
        col_name = col_list[index].name
        col_name = ATTACKERS + "{}/{} ⚔️".format(str(len(sign_list[index])), col_name[13])
    elif category == 'bishop':
        index = 1
        sign_list[index].append(name)
        col_name = col_list[index].name
        col_name = BISHOPS + "{}/{} ⚔️".format(str(len(sign_list[index])), col_name[11])
    elif category == 'buyer':
        index = 2
        sign_list[index].append(name)
        col_name = col_list[index].name
    else: 
        await (ctx.send('Invalid party role'))
        return
    embeds[0].set_field_at(index, name=col_name, value='\n'.join(sign_list[index]))
    await msg.edit(embed = embeds[0])
    guilddict[guildID][3] = sign_list
    write()

@bot.command(passContext=True)
async def remove(ctx, *, args):
    global guilddict
    guildID = str(ctx.guild.id)
    sign_list = guilddict[guildID][3]
    args = args.split(" ", 1)
    category = args[0]
    name = args[1]
    channel = bot.get_channel(int(guilddict[guildID][0]))
    msg = await channel.fetch_message(guilddict[guildID][4])
    embeds = msg.embeds
    col_list = embeds[0].fields
    if category == 'attacker':
        index = 0
        try: sign_list[index].remove(name)
        except ValueError: await(ctx.send('Could not find {} in the {} column.'.format(name, category)))
        col_name = col_list[index].name
        col_name = ATTACKERS + "{}/{} ⚔️".format(str(len(sign_list[index])), col_name[13])
    elif category == 'bishop':
        index = 1
        try: sign_list[index].remove(name)
        except ValueError: await(ctx.send('Could not find {} in the {} column.'.format(name, category)))
        col_name = col_list[index].name
        col_name = BISHOPS + "{}/{} ⚔️".format(str(len(sign_list[index])), col_name[11])
    elif category == 'buyer':
        index = 2
        try: sign_list[index].remove(name)
        except ValueError: await(ctx.send('Could not find {} in the {} column.'.format(name, category)))        
        col_name = col_list[index].name
    else: 
        await (ctx.send('Invalid party role'))
        return
    if len(sign_list[index]) > 0: embeds[0].set_field_at(index, name=col_name, value='\n'.join(sign_list[index]))
    else: embeds[0].set_field_at(index, name=col_name, value='\u200b')
    await msg.edit(embed = embeds[0])
    guilddict[guildID][3] = sign_list 
    write()

# adds a user to the list when they react
@bot.event
async def on_reaction_add(reaction, user):
    global guilddict
    guildID = str(reaction.message.guild.id)
    sign_list = guilddict[guildID][3]
    if user.bot: return
    embeds = reaction.message.embeds
    col_list, role, col_name = embeds[0].fields, -1, ""
    # these conditions check which reaction was made and updates the section that 
    # corresponds to the reaction
    if reaction.emoji == '⚔️':
        role, tag = 0, 'Attacker'
        sign_list[role].append(user.display_name)
        col_name = col_list[role].name
        col_name = ATTACKERS + "{}/{} ⚔️".format(str(len(sign_list[role])), col_name[13]) 
    elif reaction.emoji == '🇨🇭':
        role, tag = 1, 'Bishop'
        sign_list[role].append(user.display_name)
        col_name = col_list[role].name
        col_name = BISHOPS + "{}/{} 🇨🇭".format(str(len(sign_list[role])), col_name[11]) 
    else: return  
    embeds[0].set_field_at(role, name=col_name, value='\n'.join(sign_list[role]))
    await reaction.message.edit(embed = embeds[0])
    in_id = guilddict[str(reaction.message.guild.id)][1]
    await (reaction.message.guild.get_channel(in_id).send('[{}] {} has signed up for the Zak run'.format(tag, user.display_name)))
    guilddict[guildID][3] = sign_list 
    write()
#Attackers: 0/9
# handles removing a user from the list when they un-react
@bot.event
async def on_reaction_remove(reaction, user):
    global guilddict
    guildID = str(reaction.message.guild.id)
    sign_list = guilddict[guildID][3]
    if user.bot: return
    embeds = reaction.message.embeds
    col_list, role, col_name = embeds[0].fields, -1, ""
    # these conditions check which reaction was made and updates the section that 
    # corresponds to the reaction
    if reaction.emoji == '⚔️':
        role, tag = 0, 'Attacker'
        try: sign_list[role].remove(user.display_name)
        except ValueError: return
        col_name = col_list[role].name
        col_name = ATTACKERS + "{}/{} ⚔️".format(str(len(sign_list[role])), col_name[13]) 
    elif reaction.emoji == '🇨🇭':
        role, tag = 1, 'Bishop'
        try: sign_list[role].remove(user.display_name)
        except ValueError: return
        col_name = col_list[role].name
        col_name = BISHOPS + "{}/{} 🇨🇭".format(str(len(sign_list[role])), col_name[11]) 
    else: return  
    if len(sign_list[role]) > 0: embeds[0].set_field_at(role, name=col_name, value='\n'.join(sign_list[role]))
    else: embeds[0].set_field_at(role, name=col_name, value='\u200b')
    await reaction.message.edit(embed = embeds[0])
    in_id = guilddict[str(reaction.message.guild.id)][1]
    await (reaction.message.guild.get_channel(in_id).send('[{}] {} has removed themselves from the Zak run'.format(tag, user.display_name)))
    guilddict[guildID][3] = sign_list
    write()

@bot.command()
async def toggleMention(ctx):
    global guilddict
    guildid = str(ctx.guild.id)
    try: toggle = guilddict[guildid][2]
    except IndexError: toggle = True
    if toggle: 
        toggle = False
        await (ctx.send('Mentions have been turned off.'))
    else: 
        toggle = True
        await (ctx.send('Mentions have been turned on.')) 
    guilddict[guildid][2] = toggle
    write()

# helper
def makeEmbed(title, urlZak, desc, namefield1, namefield2, namefield3):
    embed = discord.Embed(title=title, description = desc)
    embed.set_thumbnail(url=urlZak)
    embed.add_field(name = namefield1, value='\u200b', inline = True)
    embed.add_field(name = namefield2, value='\u200b', inline = True)
    embed.add_field(name = namefield3, value='\u200b', inline = True)
    return embed

# helper
def isDigit(c):
    if (c>='0' and c<='9'): return True
    else: return False

def write():
    global guilddict
    with open(jsonfile, 'w') as fp:
        json.dump(guilddict, fp)
    fp.close()

bot.run(bottoken)