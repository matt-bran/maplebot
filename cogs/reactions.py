import discord
from discord.ext import commands

ATTACKERS, BISHOPS, LOOTERS = 'Attackers: ', 'Bishops: ', 'Helms 🪖'

class Reactions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guilddict = bot.guilddict

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot: return
        await self.update_sign_list(reaction, user, True)

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        if user.bot: return
        await self.update_sign_list(reaction, user, False)

    async def update_sign_list(self, reaction, user, is_add):
        guildID = str(reaction.message.guild.id)
        sign_list = self.guilddict[guildID][3]
        embeds = reaction.message.embeds
        col_list, role, col_name, tag = embeds[0].fields, -1, "", ""

        if reaction.emoji == '⚔️':
            role, tag = 0, 'Attacker'
            if is_add: sign_list[role].append(user.display_name)
            else: sign_list[role].remove(user.display_name)
            col_name = col_list[role].name
            col_name = ATTACKERS + "{}/{} ⚔️".format(str(len(sign_list[role])), col_name[13])
        elif reaction.emoji == '🇨🇭':
            role, tag = 1, 'Bishop'
            if is_add: sign_list[role].append(user.display_name)
            else: sign_list[role].remove(user.display_name)
            col_name = col_list[role].name
            col_name = BISHOPS + "{}/{} 🇨🇭".format(str(len(sign_list[role])), col_name[11])
        elif reaction.emoji == '🪖':
            role, tag = 2, 'Helms'
            if is_add: sign_list[role].append(user.display_name)
            else: sign_list[role].remove(user.display_name)
            col_name = col_list[role].name
        else: return

        embeds[0].set_field_at(role, name=col_name, value='\n'.join(sign_list[role]) if sign_list[role] else '\u200b')
        await reaction.message.edit(embed=embeds[0])

        in_id = self.guilddict[guildID][1]
        action = "signed up for" if is_add else "removed themselves from"
        await reaction.message.guild.get_channel(in_id).send(f'[{tag}] {user.display_name} has {action} the Zak run')
        self.guilddict[guildID][3] = sign_list

def setup(bot):
    bot.add_cog(Reactions(bot))