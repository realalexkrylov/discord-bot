import discord
import logging
from discord.ext import commands
from config import TOKEN
import sqlite3

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
con = sqlite3.connect('database\\discord.db')
cur = con.cursor()


class BotClient(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())

        @self.command(name="user_info")
        async def user_info_command(ctx, user: discord.Member = None):
            print(f'[!] user_info command')
            if user is None:
                user = ctx.author
            embed = discord.Embed(title=f"Информация о пользователе: {user.display_name}", color=0x00ff00)
            embed.add_field(name="Имя ползователя", value=user.name, inline=True)
            embed.add_field(name="Тэг", value=user.discriminator, inline=True)
            embed.add_field(name="ID", value=user.id, inline=True)
            embed.add_field(name="Присоединился к серверу", value=user.joined_at.strftime("%m/%d/%Y %H:%M:%S"),
                            inline=True)
            embed.add_field(name="Аккаунт был создан", value=user.created_at.strftime("%m/%d/%Y %H:%M:%S"), inline=True)
            embed.add_field(name="Роли",
                            value=", ".join([role.mention for role in user.roles if role != ctx.guild.default_role]),
                            inline=False)
            await ctx.send(embed=embed)

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        for guild in self.guilds:
            print(
                f'{self.user} has connected to the following guild:\n'
                f'{guild.name}(id: {guild.id})')
        for member in guild.members:
            print(member)

    async def on_voice_state_update(self, member, before, after):
        print(member.id)
        print(before)
        print(after)
        voice_name_request = f'SELECT voice_name FROM voice WHERE user_id = "{str(member.id)}"'
        voice_name = (cur.execute(voice_name_request).fetchall()[0])[0]
        print(voice_name)

        if after.channel:
            if after.channel.name == "Start Channel":
                guild = member.guild
                category = after.channel.category
                new_channel = await guild.create_voice_channel(f"{voice_name}", category=category)
                await member.move_to(new_channel)

        if before.channel is not None and before.channel.name == f"{voice_name}" and len(before.channel.members) == 0:
            await before.channel.delete()

    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.content.lower() == "+":
            member = message.author
            role = discord.utils.get(member.guild.roles, name="вер")
            await member.add_roles(role)
        await self.process_commands(message)


bot = BotClient()
bot.run(TOKEN)
