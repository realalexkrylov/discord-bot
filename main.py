import asyncio
import datetime

import discord
import logging
from discord.ext import commands
from config import TOKEN
from discord import File
import sqlite3

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
con = sqlite3.connect('database\\discord.db')
cur = con.cursor()
bad_words = list(map(lambda x: x[0], cur.execute(f"""SELECT word FROM words""").fetchall()))
bad_words[0] = "testword"


class BotClient(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())
        self.remove_command("help")

        # информация о пользователе
        @self.command(name="user_info")
        async def user_info_command(ctx, member: discord.Member = None):
            print(f'[!] user_info command')
            if member is None:
                member = ctx.author
            embed = discord.Embed(title=f"{member.name}'s Info", color=discord.Colour.green())
            embed.set_thumbnail(url=member.display_avatar)
            embed.add_field(name="Никнейм:", value=member.name, inline=True)
            embed.add_field(name="Тэг:", value=member.discriminator, inline=True)
            embed.add_field(name="ID:", value=member.id, inline=True)
            embed.add_field(name="Зарегистрировался:", value=member.created_at.strftime("%d.%m.%Y %H:%M:%S"),
                            inline=True)
            embed.add_field(name="Присоединился:", value=member.joined_at.strftime("%d.%m.%Y %H:%M:%S"),
                            inline=True)
            embed.add_field(name="Роли:",
                            value=", ".join([role.mention for role in member.roles if role != ctx.guild.default_role]),
                            inline=True)
            await ctx.send(embed=embed)

        @self.command(name="kick")
        @commands.has_permissions(administrator=True)
        async def kick(ctx, member: discord.Member, *reason):
            if len(reason) == 0:
                reason = None
            else:
                reason = ' '.join([i for i in reason])
            await member.kick(reason=reason)
            await ctx.send(f"{member} has been kicked from the server. Reason: {reason}")

        @self.command(name='help')
        async def help(ctx):
            emb = discord.Embed(title=f"Информация о командах", color=discord.Colour.green())
            emb.add_field(name='!voice_settings', value='настройки голосового канала', inline=False)
            emb.add_field(name='!user_info', value='Информация о пользователе', inline=False)
            emb.add_field(name='!members_info', value='Информация о пользователях', inline=False)
            emb.add_field(name='!kick', value='Удаление пользователя', inline=False)
            emb.add_field(name='!mute', value='Замутить пользователя', inline=False)
            emb.add_field(name='!server_info', value='Информация о сервере', inline=False)
            await ctx.send(embed=emb)

        @self.command(name="mute")
        @commands.has_permissions(administrator=True)
        async def mute(ctx, member: discord.Member):
            role = discord.utils.get(member.guild.roles, name="Muted")
            await member.add_roles(role)
            await member.add_roles(member, role)
            embed = discord.Embed(title="User Muted!",
                                  description="{0} was muted by {1}!".format(member, ctx.message.author),
                                  color=discord.Colour.green())
            await ctx.send(embed=embed)

        @self.command(name='server_info')
        async def server_info(ctx):
            server = ctx.guild
            embed = discord.Embed(title=f"Информация о сервере {server.name}", color=discord.Colour.green(),
                                  timestamp=datetime.datetime.now())
            embed.set_thumbnail(url=server.icon)
            embed.add_field(name="ID сервера:", value=server.id, inline=True)
            embed.add_field(name="Был создан:", value=server.created_at.strftime("%d.%m.%Y %H:%M:%S"), inline=True)
            embed.add_field(name="Количество участников:", value=server.member_count, inline=True)
            embed.add_field(name='Роли:',
                            value=", ".join(
                                [role.mention for role in server.roles if role != ctx.guild.default_role]),
                            inline=True)
            await ctx.send(embed=embed)

        # настройки войса
        @self.command(name='voice')
        async def voice_settings(ctx, setting, *args):
            user = ctx.author
            voice_channel = ctx.author.voice
            voice_id = (cur.execute(f"SELECT voice_id FROM voice WHERE user_id == '{user.id}'").fetchall()[0])[0]
            if voice_channel != None:
                if str(voice_channel.channel.id) == str(voice_id):
                    if setting == "name":
                        name = ' '.join([i for i in args])
                        if len(name) <= 24:
                            update = f"UPDATE voice " \
                                     f"SET voice_name = '{name}' " \
                                     f"WHERE user_id == '{str(user.id)}'"
                            cur.execute(update).fetchall()
                            con.commit()
                            await voice_channel.channel.edit(name=name)
                            await ctx.send("Успешно")
                        else:
                            await ctx.send("Слишком длинное название")
                    elif setting == "limit":
                        if len(args) == 1 and args[0].isdigit():
                            limit = int(args[0])
                            if 0 < limit < 100:
                                await voice_channel.channel.edit(user_limit=limit)
                                update = f"UPDATE voice " \
                                         f"SET voice_limit = {limit} " \
                                         f"WHERE user_id == '{str(user.id)}'"
                            else:
                                await voice_channel.channel.edit(user_limit=None)
                                update = f"UPDATE voice " \
                                         f"SET voice_limit = NULL " \
                                         f"WHERE user_id == '{str(user.id)}'"
                            cur.execute(update).fetchall()
                            con.commit()
                            await ctx.send(f"Успешно")
                        else:
                            await ctx.send(f"Неккоректный лимит. Введите число от 1 до 99")
                    elif setting == 'eject':
                        if len(args) == 1:
                            pass
                else:
                    await ctx.send("Вы должны находиться в своём голосовом канале")
            else:
                await ctx.send("Вы должны находиться в своём голосовом канале")

        @self.command(name='members_info')
        async def members_info(ctx, *args):
            if len(args) == 0 or ' '.join([i for i in args]) not in ['members only', 'members and bots']:
                await ctx.send(
                    'Введите аргумент **members only** или **members and bots**, чтобы получить информацию о'
                    ' пользователях')
                return
            file_path = f'data\\members_{datetime.datetime.now().strftime("%d-%m-%Y")}.txt'
            with open(file_path, 'w') as file:
                user_delay = (len(max([str(member.id) for member in ctx.guild.members]))) + 1
                file.write(f'User id{" " * (user_delay - 6)}|Join date  |Create date |Bot   |Roles |Username\n')
                if len(args) == 2 and 'members only' == ' '.join([i for i in args]):
                    for member in ctx.guild.members:
                        if not member.bot:
                            file.write(f'{str(member.id)}{" " * (user_delay - len(str(member.id)))} |'
                                       f'{str(member.joined_at.strftime("%d.%m.%Y"))} |'
                                       f'{str(member.created_at.strftime("%d.%m.%Y"))}  |'
                                       f'{str(member.bot)} |'
                                       f'{str(len([role for role in member.roles if role != ctx.guild.default_role]))}'
                                       f'     |{str(member.name)}#{str(member.discriminator)}\n')
                elif len(args) == 3 and 'members and bots' == ' '.join([i for i in args]):
                    for member in ctx.guild.members:
                        file.write(f'{str(member.id)}{" " * (user_delay - len(str(member.id)))} |'
                                   f'{str(member.joined_at.strftime("%d.%m.%Y"))} |'
                                   f'{str(member.created_at.strftime("%d.%m.%Y"))}  |'
                                   f'{str(member.bot)}{" " * (5 - len(str(member.bot)))} |'
                                   f'{str(len([role for role in member.roles if role != ctx.guild.default_role]))}'
                                   f'     |{str(member.name)}#{str(member.discriminator)}\n')
            await ctx.send(file=File(file_path))

    # дебаг + добавление пользователей которых нет в БД

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        for guild in self.guilds:
            print(
                f'{self.user} has connected to the following guild:\n'
                f'{guild.name} (id: {guild.id})')
        ids = [i[0] for i in cur.execute(f"SELECT user_id FROM voice").fetchall()]
        ids_users = [i[0] for i in cur.execute(f"SELECT user_id FROM users").fetchall()]
        for member in guild.members:
            if str(member.id) not in ids and not member.bot:
                cur.execute(f"INSERT INTO voice(user_id, voice_name) "
                            f"VALUES('{str(member.id)}', "
                            f"'{member.name}`s Chanell')").fetchall()
                con.commit()
            if str(member.id) not in ids_users and not member.bot:
                cur.execute(f"INSERT INTO users(user_mention, user_id, user_warns) "
                            f"VALUES('{str(member.name)}#{str(member.discriminator)}', '{str(member.id)}',"
                            f" 0)").fetchall()
                con.commit()

    async def on_member_join(self, member):
        ids = [i[0] for i in cur.execute(f"SELECT user_id FROM voice").fetchall()]
        if str(member.id) not in ids and not member.bot:
            cur.execute(f"INSERT INTO voice(user_id, voice_name) "
                        f"VALUES('{str(member.id)}', "
                        f"'{member.name}`s Chanell')").fetchall()
            con.commit()

    # создание нового войса и удаление
    async def on_voice_state_update(self, member, before, after):
        voice_name_request = f'SELECT voice_name, voice_limit FROM voice WHERE user_id = "{str(member.id)}"'
        response = (cur.execute(voice_name_request).fetchall()[0])
        voice_name = response[0]
        if response[1] != None:
            voice_limit = int(response[1])
        else:
            voice_limit = 'NULL'
        if after.channel:
            if after.channel.name == "Start Channel":
                guild = member.guild
                category = after.channel.category
                if voice_limit == 'NULL':
                    new_channel = await guild.create_voice_channel(f"{voice_name}", category=category)
                else:
                    new_channel = await guild.create_voice_channel(f"{voice_name}", user_limit=voice_limit,
                                                                   category=category)
                update = f"UPDATE voice " \
                         f"SET voice_id = '{new_channel.id}'" \
                         f"WHERE user_id == '{str(member.id)}'"
                cur.execute(update)
                con.commit()
                await member.move_to(new_channel)

        if before.channel is not None and before.channel.name == f"{voice_name}" and len(
                before.channel.members) == 0:
            await before.channel.delete()

    async def mute_user(self, ctx, member: discord.Member, time: int):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.add_roles(muted_role, reason="Reason for mute")
        await ctx.send(f"{member} has been muted for {time} seconds.")
        await asyncio.sleep(time)
        await member.remove_roles(muted_role, reason="Mute expired")
        await ctx.send(f"{member}'s mute has expired.")

    # реакции на сообщения
    async def on_message(self, message):
        global bad_words
        bad = False
        if message.author == self.user:
            return
        if message.content.lower() == "+":
            member = message.author
            role = discord.utils.get(member.guild.roles, name="вер")
            await member.add_roles(role)
        for bad_word in bad_words:
            if bad_word in message.content.lower():
                bad = True
                break
        if bad:
            await message.delete()
            warns = cur.execute(f'SELECT user_warns FROM users WHERE user_id == "{message.author.id}"').fetchall()[0]
            if warns[0] + 1 == 3:
                await message.channel.send("Вы нарушали слишком много, подумайте над своим поведением.")
                update = f"UPDATE users " \
                         f"SET user_warns = 0 " \
                         f"WHERE user_id == '{str(message.author.id)}'"
                cur.execute(update).fetchall()
                con.commit()
                member = message.author
                role = discord.utils.get(member.guild.roles, name="Muted")
                await member.add_roles(role)

            else:
                await message.channel.send(f"Попрошу не ругаться. Вы получаете предупреждение. {warns[0] + 1}/3")
                update = f"UPDATE users " \
                         f"SET user_warns = {warns[0] + 1} " \
                         f"WHERE user_id == '{str(message.author.id)}'"
                cur.execute(update).fetchall()
                con.commit()
        for role in message.author.roles:
            if role.name == "Muted":
                await message.delete()
                await message.channel.send("Вы находитесь в муте")

        await self.process_commands(message)


def main():
    bot = BotClient()
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
