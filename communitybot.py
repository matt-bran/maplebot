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

intents = discord.Intents(messages = True, guilds = True, reactions = True, members = True, presences = True)
bot = commands.Bot(command_prefix = '-', intents = intents)

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

# Initialize the channel that the user wants the boss run
# sign up sheet sent to from now on
@bot.command()
async def output(ctx, out_id):
    exists = False
    for channel in ctx.guild.text_channels:
        ch_name = channel.name
        channelid = channel.id 
        if str(channelid) == out_id: 
            exists = True
            break
    if not exists: return
    guildID = str(ctx.guild.id)
    guilddict[guildID] = out_id
    await(ctx.send('Output has been set to: ' + ch_name))
    with open(jsonfile, 'w') as fp:
        json.dump(guilddict, fp)

# Takes two integers for desired * of attackers and bishops 
# followed by a "sentence in qoutes" as a description and creates
# a reaction based sign up sheet for Zakum boss runs. 
@bot.command(pass_context=True)
async def zak(ctx, *, args):
    guild = ctx.guild
    guildID = str(ctx.guild.id)
    try:
        out_id = guilddict[guildID]
    except KeyError:
        await ctx.send(content="The output channel hasn't been set. Use `-output channelID`. Right click the channel you want to send to and copy the id.")
        return
    att_lim, bsh_lim, desc = args[0], args[2], args[3:]
    if not isDigit(att_lim) or not isDigit(bsh_lim): return
    embed = makeEmbed("Zakum runs", urlZak, desc, "Attackers: 0/{} ⚔️".format(att_lim), "Bishops: 0/{} 🇨🇭".format(bsh_lim), 'Helms 🪖')
    embed.set_author(name=ctx.author.display_name + " is hosting", icon_url=ctx.author.avatar_url)
    boss_role = discord.utils.get(guild.roles, name="Bossing")
    helm_role = discord.utils.get(guild.roles, name="Zakum Helmet")
    roles = [boss_role, helm_role]
    out_channel = guild.get_channel(int(out_id))
    message = await out_channel.send(content="".join(role.mention for role in roles),embed=embed)
    await message.add_reaction('⚔️')
    await message.add_reaction('🇨🇭')
    await message.add_reaction('🪖')

# adds a user to the list when they react
@bot.event
async def on_reaction_add(reaction, user):
    if user.bot: return
    embeds = reaction.message.embeds
    field_list = embeds[0].fields
    field_index = -1
    field_name = ""
    # these conditions check which reaction was made and updates the section that 
    # corresponds to the reaction
    if reaction.emoji == '⚔️':
        field_index = 0
        replace_indx = 11
        field_name = field_list[field_index].name
        field_name = field_name[:replace_indx] + str(int(field_name[replace_indx]) + 1) + field_name[replace_indx + 1:]
    elif reaction.emoji == '🇨🇭':
        field_index = 1
        replace_indx = 9
        field_name = field_list[field_index].name
        field_name = field_name[:replace_indx] + str(int(field_name[replace_indx]) + 1) + field_name[replace_indx + 1:]
    elif reaction.emoji == '🪖':
        field_index = 2
        field_name = field_list[field_index].name
    else: return  
    value_str = field_list[field_index].value
    value_str = add(value_str, user)
    embeds[0].set_field_at(field_index, name = field_name, value=value_str)
    await reaction.message.edit(embed = embeds[0])

# handles removing a user from the list when they un-react
@bot.event
async def on_reaction_remove(reaction, user):
    if user.bot: return
    embeds = reaction.message.embeds
    field_list = embeds[0].fields
    field_index = -1
    field_name = ""
    # these conditions check which reaction was made and updates the section that 
    # corresponds to the reaction
    if reaction.emoji == '⚔️':
        field_index = 0
        replace_indx = 11
        field_name = field_list[field_index].name
        field_name = field_name[:replace_indx] + str(int(field_name[replace_indx]) - 1) + field_name[replace_indx + 1:]
    elif reaction.emoji == '🇨🇭':
        field_index = 1
        replace_indx = 9
        field_name = field_list[field_index].name
        field_name = field_name[:replace_indx] + str(int(field_name[replace_indx]) - 1) + field_name[replace_indx + 1:]
    elif reaction.emoji == '🪖':
        field_index = 2
        field_name = field_list[field_index].name
    else: return  
    value_str = field_list[field_index].value
    value_str = rem(value_str, user)
    embeds[0].set_field_at(field_index, name = field_name, value=value_str)
    await reaction.message.edit(embed = embeds[0])

# helper
def makeEmbed(title, urlZak, desc, namefield1, namefield2, namefield3):
    embed = discord.Embed(title=title, description = desc)
    embed.set_thumbnail(url=urlZak)
    embed.add_field(name = namefield1, value='\u200b', inline = True)
    embed.add_field(name = namefield2, value='\u200b', inline = True)
    embed.add_field(name = namefield3, value='\u200b', inline = True)
    return embed
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