from discord.ext import commands

class ServerSettings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guilddict = bot.guilddict

    @commands.command()
    # Initialize the channel that the user wants the boss run
    # sign up sheet sent to from now on
    async def output(self, ctx, out_id):
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

    # Initialize the channel that the user wants the boss run
    # sign up sheet sent to from now on
    @commands.command()
    async def input(self, ctx):
        guildID = str(ctx.guild.id)
        self.guilddict[guildID][1] = ctx.channel.id
        await(ctx.send('Input has been set. Logs will be sent to: {}'.format(ctx.channel.name)))

    @commands.command()
    async def toggleMention(self, ctx):
        guildid = str(ctx.guild.id)
        try: toggle = self.guilddict[guildid][2]
        except IndexError: toggle = True
        if toggle: 
            toggle = False
            await (ctx.send('Mentions have been turned off.'))
        else: 
            toggle = True
            await (ctx.send('Mentions have been turned on.')) 
        self.guilddict[guildid][2] = toggle

def setup(bot):
    bot.add_cog(ServerSettings(bot))