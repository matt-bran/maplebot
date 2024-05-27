from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        help_message = [
            '-add <party role> <name entry> | Adds the name entry to the specified party role (attacker, bishop, helm).',
            '-remove <party role> <name entry> | Removes the name entry from the specified party role.',
            '-input | Sets the current channel to receive sign-up log messages.',
            '-output <bossing channel id> | Sets the channel to send the bossing sheet to.',
            '-toggleMention | Toggles mentions in the sign-up sheet. On by default.'
        ]
        await ctx.send(('```' + '\n'.join(help_message) + '```'))

def setup(bot):
    bot.add_cog(Help(bot))
