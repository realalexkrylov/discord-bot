import asyncio
import logging
import random

import discord
from discord.ext import commands

from config import TOKEN

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
dashes = ['\u2680', '\u2681', '\u2682', '\u2683', '\u2684', '\u2685']


class RandomThings(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='roll_dice')
    async def roll_dice(self, ctx, count):
        res = [random.choice(dashes) for _ in range(int(count))]
        await ctx.send(" ".join(res))

    @commands.command(name='randint')
    async def my_randint(self, ctx, min_int, max_int):
        num = random.randint(int(min_int), int(max_int))
        await ctx.send(num)


bot = commands.Bot(command_prefix='!#', intents=intents)


async def main():
    await bot.add_cog(RandomThings(bot))
    await bot.start(TOKEN)


asyncio.run(main())
