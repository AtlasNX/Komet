import discord
from discord.ext import commands
from sys import argv

class Links:
    """
    Commands for easily linking to projects.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

        
    @commands.command()
    async def kosmos(self):
        """Kosmos"""
        await self.bot.say("https://github.com/AtlasNX/Kosmos")

    @commands.command()
    async def guide(self):
        """Guide"""
        await self.bot.say("https://guide.teamatlasnx.com")

    @commands.command()
    async def patreon(self):
        """Patreon"""
        await self.bot.say("https://patreon.teamatlasnx.com")
    
def setup(bot):
    bot.add_cog(Links(bot))
