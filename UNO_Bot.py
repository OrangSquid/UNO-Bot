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
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(
    '[%(asctime)s]: %(levelname)s: %(name)s: %(message)s'))
logger.addHandler(handler)


async def prefix(bot, message) -> str:
    return "uno "

# Global variables to keep track of games and who's WAITING
WAITING: Dict[discord.Guild, List[discord.User]] = {}
PLAYING: Dict[discord.Guild, uno_core.Uno] = {}
# Keep track of DEFINITIONS and card info like the emojis and images
DEFINITIONS: Dict[Any, Any] = {}
CARD_INFO: Dict[str, List[Any]] = {}
uno_bot = commands.Bot(command_prefix=prefix)


async def look_for_player(caller: discord.User) -> bool:
    # Looks if the caller of either join or play_uno is already in a game to avoid confusion in DMs with the bot
    for game in PLAYING.values():
        for player in game.order:
            if player.user == caller:
                return True
    for lobby in WAITING.values():
        for player in lobby:
            if player == caller:
                return True
    else:
        return False


@uno_bot.command(help="Lets you create a new lobby for a UNO game")
@commands.guild_only()
async def play(ctx):
    # Checks if there's already a game WAITING to start
    # If not, make a new one
    # Else if it is the first issuer of the command, start the game,
    # Else join the game

    # Check if there's a game waiting
    try:
        WAITING[ctx.guild]
    except KeyError:
        # Check if there's a game in course
        try:
            PLAYING[ctx.guild]
        # Join the game
        except KeyError:
            if await look_for_player(ctx.author):
                await ctx.send(":x: You are already in a game in this or in another server!")
            else:
                WAITING[ctx.guild] = [ctx.author]
                embed_to_send = discord.Embed(title="Game WAITING",
                                              description="If you want to join the game, use uno play."
                                                          "\nOnce you want to start, {} should use uno play."
                                                          "\nUp to four players can join.".format(ctx.author),
                                              timestamp=datetime.datetime.now())
                embed_to_send.set_author(name="{.author} wants to start a game!".format(ctx),
                                         icon_url=str(ctx.author.avatar_url))
                embed_to_send.set_footer(
                    text="UNO Game at \"{.guild}\"".format(ctx))
                await ctx.send(embed=embed_to_send)
        else:
            print("There's a game in course in this server!")
    # Make a game or join it
    else:
        if ctx.author == WAITING[ctx.guild][0]:
            if len(WAITING[ctx.guild]) == 1:
                await ctx.send(":grey_exclamation: There aren't enough players to start. You need at least 2.")
            else:
                players = []
                for player in WAITING[ctx.guild]:
                    players.append(uno_core.Player(player))
                game = uno_core.Uno(players, DEFINITIONS[str(
                    ctx.guild.id)], CARD_INFO, ctx.channel, uno_bot)
                PLAYING[ctx.guild] = game
                WAITING.pop(ctx.guild)
                await game.play_game()
                PLAYING.pop(ctx.guild)
        elif ctx.author in WAITING[ctx.guild]:
            await ctx.send(":x: You are already WAITING for the game! The first caller of the play command should be the one to start.")
        elif await look_for_player(ctx.author):
            await ctx.send(":x: You are already in a game in this or in another server!")
        else:
            if len(WAITING[ctx.guild]) != 20:
                WAITING[ctx.guild].append(ctx.author)
                await ctx.send(
                    ":white_check_mark: {} has joined the game ({}/20)".format(ctx.author.mention,
                                                                               len(WAITING[ctx.guild])))
            else:
                await ctx.send(":x: The game is already full")

@uno_bot.command(help="Lets you leave the lobby you're in")
@commands.guild_only()
async def leave(ctx):
    try:
        WAITING[ctx.guild].remove(ctx.author)
        await ctx.send(":white_check_mark: {.author.mention} "
                       "has been removed from the game ({}/20)".format(ctx, len(WAITING[ctx.guild])))
    except KeyError:
        await ctx.send(":x: You are not WAITING for any game!")


@uno_bot.command(help="Lets you stop the lobby or the game you're PLAYING")
@commands.guild_only()
async def stop(ctx):
    try:
        WAITING.pop(ctx.guild)
        await ctx.send(":grey_exclamation: Your game has been cancelled")
    except KeyError:
        try:
            await ctx.send("The game will stop after next player's turn")
            PLAYING[ctx.guild].stop = True
        except KeyError:
            await ctx.send(":x: There are no games to stop")


@uno_bot.command(help="Lets you stop the lobby or the game you're PLAYING")
@commands.guild_only()
async def debug(ctx):
    player = uno_core.Player(ctx.author)
    game = uno_core.Uno([player, player], DEFINITIONS[str(
        ctx.guild.id)], CARD_INFO, ctx.channel, uno_bot)
    PLAYING[ctx.guild] = game
    await game.play_game()
    PLAYING.pop(ctx.guild)


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
    if change:
        await ctx.send("You must now skip after a 2+ or 4+ card")
    else:
        await ctx.send("You can now play after a 2+ or 4+ card")


@settings.command()
async def must_play(ctx, change: bool):
    await change_settings("must_play", change, ctx.guild.id)
    if change:
        await ctx.send("You can now play after drawing a card you can play")
    else:
        await ctx.send("You must now skip a turn after drawing a card")


@settings.command()
async def stacking(ctx, change: bool):
    await change_settings("stacking", change, ctx.guild.id)
    if change:
        await ctx.send("You can now stack 2+'s")
    else:
        await ctx.send("You can't stack 2+'s")


async def change_settings(setting: str, to_change, guild_id: int):
    DEFINITIONS[str(guild_id)][setting] = to_change
    with open("DEFINITIONS.json", "w") as file:
        json.dump(DEFINITIONS, file, indent="\t")


@uno_bot.event
async def on_ready():
    global DEFINITIONS
    global CARD_INFO
    # Loading the card info file
    with open("info.json", "r") as file:
        CARD_INFO = json.load(file)
        for x in zip(CARD_INFO.keys(), CARD_INFO.values()):
            CARD_INFO[x[0]][1] = uno_bot.get_emoji(x[1][1])
    # Loading the DEFINITIONS file and filling in any guild missing
    with open("DEFINITIONS.json", "r") as file:
        DEFINITIONS = json.load(file)
        for guild in uno_bot.guilds:
            try:
                DEFINITIONS[str(guild.id)]
            except KeyError:
                DEFINITIONS[guild.id] = DEFINITIONS["default"]
    with open("DEFINITIONS.json", "w") as file:
        json.dump(DEFINITIONS, file, indent="\t")
    print("We are ready to roll!")


@uno_bot.event
async def on_guild_join(guild):
    DEFINITIONS[guild.id] = DEFINITIONS["default"]
    with open("DEFINITIONS.json.json", "w") as file:
        json.dump(DEFINITIONS, file, indent="\t")


def main():
    with open("Token.txt", "r") as token:
        uno_bot.run(token.read())


if __name__ == "__main__":
    main()
