import logging
import uno_core
import discord
import datetime
import json
from discord.ext import commands
from typing import Dict, List, Any

# Setting up the logger function for the library
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('[%(asctime)s]: %(levelname)s: %(name)s: %(message)s'))
logger.addHandler(handler)


# TODO: add a way to change the command prefix (maybe?)
async def prefix(bot, message) -> str:
    return "uno "


# Global variables to keep track of games and who's waiting
waiting: Dict[discord.Guild, List[discord.User]] = {}
playing: Dict[discord.Guild, uno_core.Uno] = {}
CARD_INFO: Dict[str, List[Any]] = {}
uno_bot = commands.Bot(command_prefix=prefix)


async def look_for_player(caller: discord.User) -> bool:
    # Looks if the caller of either join or play_uno is already in a game to avoid confusion in DMs with the bot
    for game in playing.values():
        for player in game.order:
            if player.user == caller:
                return True
    for lobby in waiting.values():
        for player in lobby:
            if player == caller:
                return True
    else:
        return False


@uno_bot.command(help="Lets you create a new lobby for a UNO game")
@commands.guild_only()
async def play(ctx):
    # Checks if there's already a game waiting to start
    # If not, make a new one
    try:
        print(waiting[ctx.guild])
    except KeyError:
        try:
            print(playing[ctx.guild])
        except KeyError:
            if await look_for_player(ctx.author):
                await ctx.send(":x: You are already in a game in this or in another server!")
            else:
                waiting[ctx.guild] = [ctx.author]
                embed_to_send = discord.Embed(title="Game Waiting",
                                              description="If you want to join the game, use uno join."
                                                          "\nOnce you want to start, use uno start."
                                                          "\nUp to six players can join.",
                                              timestamp=datetime.datetime.now())
                embed_to_send.set_author(name="{.author} wants to start a game!".format(ctx),
                                         icon_url=str(ctx.author.avatar_url))
                embed_to_send.set_thumbnail(url="https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck"
                                                "/logo.png")
                embed_to_send.set_footer(text="UNO Game at \"{.guild}\"".format(ctx))
                await ctx.send(embed=embed_to_send)
    else:
        await ctx.send(":x: There's already a game waiting to start or one is already on course")


@uno_bot.command(help="Lets you join the current UNO lobby in your server")
@commands.guild_only()
async def join(ctx):
    try:
        if ctx.author in waiting[ctx.guild]:
            await ctx.send(":x: You are already waiting for the game")
        elif await look_for_player(ctx.author):
            await ctx.send(":x: You are already in a game in this or in another server!")
        else:
            if len(waiting[ctx.guild]) != 6:
                waiting[ctx.guild].append(ctx.author)
                await ctx.send(
                    ":white_check_mark: {} has joined the game ({}/6)".format(ctx.author.mention,
                                                                              len(waiting[ctx.guild])))
            else:
                await ctx.send(":x: The game is already full")
    except KeyError:
        await ctx.send(":x: There are no current games waiting to start")


@uno_bot.command(help="If there's a lobby with enough people in it, then this command will start the game")
@commands.guild_only()
async def start(ctx):
    try:
        if len(waiting[ctx.guild]) == 1:
            await ctx.send(":grey_exclamation: There aren't enough players to start. You need at least 2.")
        else:
            players = []
            for player in waiting[ctx.guild]:
                players.append(uno_core.Player(player))
            game = uno_core.Uno(players, CARD_INFO, ctx.channel, uno_bot)
            playing[ctx.guild] = game
            waiting.pop(ctx.guild)
            await game.play_game()
            playing.pop(ctx.guild)
    except KeyError:
        await ctx.send(":x: There's no game to start!")


@uno_bot.command(help="Lets you leave the lobby you're in")
@commands.guild_only()
async def leave(ctx):
    try:
        waiting[ctx.guild].remove(ctx.author)
        await ctx.send(":white_check_mark: {.author.mention} "
                       "has been removed from the game ({}/6)".format(ctx, len(waiting[ctx.guild])))
    except KeyError:
        await ctx.send(":x: You are not waiting for any game!")


@uno_bot.command(help="Lets you stop the lobby or the game you're playing")
@commands.guild_only()
async def stop(ctx):
    try:
        waiting.pop(ctx.guild)
        await ctx.send(":grey_exclamation: Your game has been cancelled")
    except KeyError:
        try:
            playing[ctx.guild].stop = True
        except KeyError:
            await ctx.send(":x: There are no games to stop")


@uno_bot.command(enabled=False)
async def settings(ctx):
    pass


@uno_bot.event
async def on_ready():
    global CARD_INFO
    with open("settings.json") as settings_json:
        temp_info = json.load(settings_json)
        for x in zip(temp_info["CARD INFO"].keys(), temp_info["CARD INFO"].values()):
            temp_info["CARD INFO"][x[0]][1] = uno_bot.get_emoji(x[1][1])
        CARD_INFO = temp_info["CARD INFO"]
    print("We are ready to roll!")


def main():
    with open("Token.txt", "r") as token:
        uno_bot.run(token.read())


if __name__ == "__main__":
    main()
