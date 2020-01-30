import discord
import logging
import random
import UNO_Core
import json
from discord.ext import commands

# Setting up the logger function for the library
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('[%(asctime)s]: %(levelname)s: %(name)s: %(message)s'))
logger.addHandler(handler)


# TODO: add a way to change the command prefix
async def prefix(bot, message):
    return "!"


# Global variables to keep track of games and who's waiting
WAITING = {}
PLAYING = {}
uno_bot = commands.Bot(command_prefix=prefix)


@uno_bot.command()
async def play_uno(ctx):
    # Checks if there's already a game waiting to start
    # If not, make a new one
    try:
        WAITING[ctx.guild]
    except KeyError:
        WAITING[ctx.guild] = [ctx.author]
        await ctx.send("{user} wants to start a game!".format(user=ctx.author.mention))
        await ctx.send("If anybody wants to join the game, use !join")
        await ctx.send("Up to 6 players can join")
    else:
        await ctx.send("There's already a game waiting to start")


@uno_bot.command()
async def join(ctx):
    try:
        if ctx.author in WAITING[ctx.guild]:
            await ctx.send("You are already waiting for the game")
        else:
            WAITING[ctx.guild].append(ctx.author)
            await ctx.send("{user} has joined the game".format(ctx.user.mention))
    except KeyError:
        await ctx.send("There are no current games waiting to start")


@uno_bot.command()
async def start(ctx):
    players = []
    try:
        for player in WAITING[ctx.guild]:
            players.append(UNO_Core.Player(player))
        game = UNO_Core.Uno(players, ctx.guild)
        PLAYING[ctx.guild] = game
        game.play_game()
        PLAYING.pop(ctx.guild)
    except KeyError:
        await ctx.send("There's no game to start!")


@uno_bot.command()
async def stop(ctx):
    pass


@uno_bot.command()
async def settings(ctx):
    pass


@uno_bot.event
async def on_ready():
    print("We are ready to roll!")


def main():
    with open("Token.txt", "r") as token:
        uno_bot.run(token.read())


if __name__ == "__main__":
    main()
