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
    if message.guild.id == 556652655397830657:
        return "owo "
    else:
        return "uno "


# Global variables to keep track of games and who's waiting
waiting: Dict[discord.Guild, List[discord.User]] = {}
playing: Dict[discord.Guild, uno_core.Uno] = {}
definitions: Dict[Any, Any] = {}
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
            game = uno_core.Uno(players, definitions[str(ctx.guild.id)], CARD_INFO, ctx.channel, uno_bot)
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


@uno_bot.group()
async def settings(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send(":x: Choose a setting! Please use uno help to get a full list of settings")


@settings.command()
async def decks(ctx, number: int):
    await change_settings("decks", number, ctx.guild.id)
    await ctx.send("The number of decks has changed to {}".format(number))


@settings.command()
async def initial_cards(ctx, number: int):
    await change_settings("initial_cards", number, ctx.guild.id)
    await ctx.send("The number of initial cards to give to each player has changed to {}".format(number))


@settings.command()
async def draw_skip(ctx, change: bool):
    await change_settings("draw_skip", change, ctx.guild.id)
    if bool:
        await ctx.send("You must now skip after a 2+ or 4+ card")
    else:
        await ctx.send("You can now play after a 2+ or 4+ card")


@settings.command()
async def must_play(ctx, change: bool):
    await change_settings("must_play", change, ctx.guild.id)
    if bool:
        await ctx.send("You can now play after drawing a card you can play")
    else:
        await ctx.send("You must now skip a turn after drawing a card")


@settings.command()
async def stacking(ctx, change: bool):
    await change_settings("stacking", change, ctx.guild.id)
    if bool:
        await ctx.send("You can now stack 2+'s")
    else:
        await ctx.send("You can't stack 2+'s")


async def change_settings(setting: str, to_change, guild_id: int):
    definitions[str(guild_id)][setting] = to_change
    with open("definitions.json", "w") as file:
        json.dump(definitions, file, indent="\t")


@uno_bot.event
async def on_ready():
    global definitions
    global CARD_INFO
    # Loading the card info file
    with open("info.json", "r") as file:
        CARD_INFO = json.load(file)
        for x in zip(CARD_INFO.keys(), CARD_INFO.values()):
            CARD_INFO[x[0]][1] = uno_bot.get_emoji(x[1][1])
    # Loading the definitions file and filling in any guild missing
    with open("definitions.json", "r") as file:
        definitions = json.load(file)
        for guild in uno_bot.guilds:
            try:
                print(definitions[str(guild.id)])
            except KeyError:
                definitions[guild.id] = definitions["default"]
    with open("definitions.json", "w") as file:
        json.dump(definitions, file, indent="\t")
    print("We are ready to roll!")


@uno_bot.event
async def on_guild_join(guild):
    definitions[guild.id] = definitions["default"]
    with open("definitions.json.json", "w") as file:
        json.dump(definitions, file, indent="\t")


def main():
    with open("Token.txt", "r") as token:
        uno_bot.run(token.read())


if __name__ == "__main__":
    main()
