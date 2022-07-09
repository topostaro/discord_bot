# ======== imports ========

from typing import List
import discord
from discord.ext import commands

import os
import re
import random

# ======== constants ========

TOKEN = os.getenv('DISCORD_TOKEN')

# ======== global states ========


intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# ======== classes ========


class Game:
    def __init__(self, channel: discord.TextChannel, players: List[discord.Member]):
        self.channel = channel
        self.demon = players[0]
        self.players = players
        self.demonic = []
        self.true_name = ""
        self.player_num = len(players)
        if self.player_num <= 6:
            self.demonic_num = 1
        else:
            self.demonic_num = 2

    async def start(self):
        await self.channel.send("ゲームを開始します")

        random.shuffle(self.players)
        self.demon = self.players[0]
        self.players = self.players[1:]

        await self.channel.send(f"悪魔は{self.demon.display_name}です")
        await self.preparation()

    async def preparation(self):
        global bot

        # 真名
        await self.demon.send("真名を入力してください")

        def check(m: discord.Message) -> bool:
            pattern = ""
            if self.player_num == 5:
                pattern = "^\d{3}$"
            else:
                pattern = "^\d{4}$"

            reselut = re.match(pattern, m.content) != None
            return reselut & (m.author == self.demon)

        self.true_name: str = (await bot.wait_for('message', check=check)).content

        # 悪魔憑き指名
        self.demonic = self.players[0:self.demonic_num]

        for demonic in self.demonic:
            await self.demon.send(f"{demonic.display_name}は悪魔憑きです")
            await demonic.send("あなたは悪魔憑きです")
            await demonic.send(f"悪魔の真名は「{self.true_name}」です")

        for i in range(self.demonic_num, self.player_num):
            exocist = self.players[i]
            await exocist.send(f"悪魔の真名の{i - self.demonic_num + 1}番目は「{self.true_name[i - self.demonic_num]}」です")

    async def round1(self):
        self.channel.send("エクソシストの皆さんは悪魔の真名を予想してください")


@bot.event
async def on_ready():
    print(f'Connected as {bot.user.name}')


@bot.command()
async def new(ctx: commands.context.Context):
    players = ctx.message.author.voice.channel.members
    channel = ctx.channel

    game = Game(channel, players)
    await game.start()


@bot.command()
async def test(ctx: commands.context.Context):
    channel = ctx.channel
    players = [ctx.message.author] * 5

    game = Game(channel, players)
    await game.start()


bot.run(TOKEN)
