import discord
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
bot.remove_command('help')

@bot.event
async def on_ready(): 
    await bot.change_presence(activity=discord.Game(name="-help"))
    print('Bot is ready.')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
async def help(ctx):
    command_list = "-help\n-splits"
    out_list = "n/a" + "\n#_of_mesos @user1 @user2 ... @userX"
    embed = discord.Embed(title = "Command Guide", color = discord.Color.red())  
    embed.add_field(name = "Command name", value = command_list, inline = True)
    embed.add_field(name = "Input format", value = out_list, inline = True)
    await ctx.send(embed=embed)

@bot.command()
async def splits(ctx, mesos, *members: discord.Member):
    if len(members) == 0:
        await ctx.send("Who are you handing splits to?")
        return
    try:  
        if ',' in mesos:
            mesos = mesos.replace(",", "")
        runner_amount = int(mesos)/len(members)
    except:
        await ctx.send("Your mesos dont look right -_-")
        return
    runners = ""
    display_amount = ""
    for i in range(len(members)):
        if not members[i].nick:
            runners += (str(members[i].name) + "\n")
        else:
            runners += (str(members[i].nick) + "\n")
        display_amount += ("{:,}".format(int(runner_amount)) + "\n")
    
        embed = discord.Embed(title = "Splits", description = "Total run amount: " + "{:,}".format(int(mesos)), color = discord.Color.red())  
    embed.add_field(name = "Runners", value = runners, inline = True)
    embed.add_field(name = "Amount", value = display_amount, inline = True)

@bot.command()
async def zak(ctx, *args):
    guild = ctx.guild
    bot_channel = 961813953078505542
    boss_channel = 801961725712400387
    if ctx.channel != guild.get_channel(bot_channel): return
    att_lim = args[0]
    bsh_lim = args[1]
    desc = args[2]
    embed = discord.Embed(title="Zakum Runs", description = desc)
    embed.set_thumbnail(url="https://static.wikia.nocookie.net/maplestory/images/f/f2/Monster_Zakum.png/revision/latest?cb=20140101121359&path-prefix=pl")
    embed.add_field(name = "Attackers: 0/{} ⚔️".format(att_lim), value='\u200b', inline = True)
    embed.add_field(name = "Bishops: 0/{} 🇨🇭".format(bsh_lim), value='\u200b', inline = True)
    embed.add_field(name = 'Helms 🪖', value='\u200b', inline = True)
    embed.set_author(name=ctx.author.display_name + " is hosting", icon_url=ctx.author.avatar_url)
    boss_role = discord.utils.get(guild.roles, name="Bossing")
    helm_role = discord.utils.get(guild.roles, name="Zakum Helmet")
    roles = [boss_role, helm_role]
    boss_channel = guild.get_channel(boss_channel)
    message = await boss_channel.send(content="".join(role.mention for role in roles),embed=embed)
    await message.add_reaction('⚔️')
    await message.add_reaction('🇨🇭')
    await message.add_reaction('🪖')

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
    if reaction.emoji == '🇨🇭':
        sec_index = 1
        replace_indx = 9
        fname = list[sec_index].name
        fname = fname[:replace_indx] + str(int(fname[replace_indx]) + 1) + fname[replace_indx + 1:]
    if reaction.emoji == '🪖':
        sec_index = 2
        fname = list[sec_index].name
    sec_list = list[sec_index].value
    sec_list = add(sec_list, user)
    embeds[0].set_field_at(sec_index, name = fname, value=sec_list)
    await reaction.message.edit(embed = embeds[0])

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
    if reaction.emoji == '🇨🇭':
        sec_index = 1
        replace_indx = 9
        fname = list[sec_index].name
        fname = fname[:replace_indx] + str(int(fname[replace_indx]) - 1) + fname[replace_indx + 1:]
    if reaction.emoji == '🪖':
        sec_index = 2
        fname = list[sec_index].name    
    sec_list = list[sec_index].value
    sec_list = rem(sec_list, user)
    embeds[0].set_field_at(sec_index, name = fname, value=sec_list)
    await reaction.message.edit(embed = embeds[0])

def add(string, user):
    if string == '\u200b': string = user.display_name
    else: string += "\n" + user.display_name
    return string

def rem(string, user):
    string = string.replace(user.display_name, '') 
    if not string: string = '\u200b'
    return string

bot.run(bottoken)