import discord
from discord.ext import commands

urlZak = "https://static.wikia.nocookie.net/maplestory/images/f/f2/Monster_Zakum.png/revision/latest?cb=20140101121359&path-prefix=pl"
ATTACKERS, BISHOPS, LOOTERS = 'Attackers: ', 'Bishops: ', 'Helms 🪖'

class Zakum(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guilddict = bot.guilddict

    @commands.command(pass_context=True)
    async def zak(self, ctx, *, args):
        guild = ctx.guild
        guildID = str(ctx.guild.id)
        try:
            out_id = self.bot.guilddict[guildID][0]
        except KeyError:
            await ctx.send("The output channel hasn't been set. Use `-output channelID`.")
            return
        args = args.split(' ', 2)
        if len(args) < 3 or not args[0].isdigit() or not args[1].isdigit():
            await ctx.send("Invalid arguments. Use: -zak <attacker_limit> <bishop_limit> <description>")
            return
        att_lim, bish_lim, desc = args[0], args[1], args[2]
        embed = self.makeEmbed("Zakum runs", urlZak, desc, ATTACKERS + f"0/{att_lim} ⚔️", 
                                                        BISHOPS + f"0/{bish_lim} 🇨🇭", LOOTERS)
        embed.set_author(name=ctx.author.display_name + " is hosting", icon_url=ctx.author.avatar_url)
        boss_role = discord.utils.get(guild.roles, name="Bossing")
        helm_role = discord.utils.get(guild.roles, name="Zakum Helmet")
        roles = [boss_role, helm_role]
        out_channel = guild.get_channel(int(out_id))
        if self.guilddict[guildID][2]:
            recentMsg = await out_channel.send(content="".join(role.mention for role in roles), embed=embed)
        else:
            recentMsg = await out_channel.send(embed=embed)
        await recentMsg.add_reaction('⚔️')
        await recentMsg.add_reaction('🇨🇭')
        await recentMsg.add_reaction('🪖')
        self.guilddict[guildID][3] = [[], [], []]
        self.guilddict[guildID][4] = recentMsg.id
    
    @commands.command(passContext=True)
    async def add(self, ctx, *, args):
        guildID = str(ctx.guild.id)
        sign_list = self.guilddict[guildID][3]
        args = args.split(" ", 1)
        category = args[0]
        name = args[1]
        channel = self.bot.get_channel(int(self.guilddict[guildID][0]))
        msg = await channel.fetch_message(self.guilddict[guildID][4])
        embeds = msg.embeds
        col_list = embeds[0].fields
        if category.lower() == 'attacker':
            index = 0
            sign_list[index].append(name)
            col_name = col_list[index].name
            col_name = ATTACKERS + "{}/{} ⚔️".format(str(len(sign_list[index])), col_name[13])
        elif category.lower() == 'bishop':
            index = 1
            sign_list[index].append(name)
            col_name = col_list[index].name
            col_name = BISHOPS + "{}/{} ⚔️".format(str(len(sign_list[index])), col_name[11])
        elif category.lower() == 'helm':
            index = 2
            sign_list[index].append(name)
            col_name = col_list[index].name
        else: 
            await (ctx.send('Invalid party role'))
            return
        embeds[0].set_field_at(index, name=col_name, value='\n'.join(sign_list[index]))
        await msg.edit(embed = embeds[0])
        self.guilddict[guildID][3] = sign_list

    @commands.command(passContext=True)
    async def remove(self, ctx, *, args):
        guildID = str(ctx.guild.id)
        sign_list = self.guilddict[guildID][3]
        args = args.split(" ", 1)
        category = args[0]
        name = args[1]
        channel = self.bot.get_channel(int(self.guilddict[guildID][0]))
        msg = await channel.fetch_message(self.guilddict[guildID][4])
        embeds = msg.embeds
        col_list = embeds[0].fields
        if category.lower() == 'attacker':
            index = 0
            try: sign_list[index].remove(name)
            except ValueError: await(ctx.send('Could not find {} in the {} column.'.format(name, category)))
            col_name = col_list[index].name
            col_name = ATTACKERS + "{}/{} ⚔️".format(str(len(sign_list[index])), col_name[13])
        elif category.lower() == 'bishop':
            index = 1
            try: sign_list[index].remove(name)
            except ValueError: await(ctx.send('Could not find {} in the {} column.'.format(name, category)))
            col_name = col_list[index].name
            col_name = BISHOPS + "{}/{} ⚔️".format(str(len(sign_list[index])), col_name[11])
        elif category.lower() == 'helm':
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
        self.guilddict[guildID][3] = sign_list 

    def makeEmbed(self, title, urlZak, desc, namefield1, namefield2, namefield3):
        embed = discord.Embed(title=title, description=desc)
        embed.set_thumbnail(url=urlZak)
        embed.add_field(name=namefield1, value='\u200b', inline=True)
        embed.add_field(name=namefield2, value='\u200b', inline=True)
        embed.add_field(name=namefield3, value='\u200b', inline=True)
        return embed
    
    def isDigit(c):
        if (c>='0' and c<='9'): return True
        else: return False

def setup(bot):
    bot.add_cog(Zakum(bot))
