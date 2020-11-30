import json
import logging
from typing import Any, Dict, List

import discord
import uno_core
from discord.ext import commands

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
EMBEDS_DICT = {}
DEFINITIONS: Dict[Any, Any] = {}
CARD_INFO: Dict[str, List[Any]] = {}
uno_bot = commands.Bot(command_prefix=prefix)


async def look_for_player(caller: discord.User) -> bool:
    # Looks if the caller of either join or play_uno is already in a game to avoid confusion in DMs with the bot
    for game in PLAYING.values():
        if caller in game.order:
            return True
    return any(caller in lobby for lobby in WAITING.values())

async def join(ctx):
    """
    Tries to join the game waiting.

    Else try to start it
    """

    wait_list = WAITING[ctx.guild]
    if ctx.author not in wait_list and len(wait_list) < 6:
        wait_list.append(ctx.author)
        await ctx.send(f'✅ {ctx.author.mention} has joined the game ({len(wait_list)}/6)')
    elif ctx.author == wait_list[0]:
        start(ctx)
    else:
        await ctx.send('❌ You\'re already in the game or the lobby is full!\n❕ Please note the first caller of the play command should call it again to begin the game')


async def start(ctx):
    """
    Starts the game provided there's one in WAITING
    """

    wait_list = WAITING[ctx.guild]
    if len(wait_list) == 1:
        await ctx.send("❕ There aren't enough players to start. You need at least 2.")
    else:
        players = [uno_core.Player(player) for player in wait_list]
        game = uno_core.Uno(players, DEFINITIONS[str(
            ctx.guild.id)], CARD_INFO, ctx.channel, uno_bot)
        PLAYING[ctx.guild] = game
        WAITING.remove(ctx.guild)
        await game.play_game()
        PLAYING.remove(ctx.guild)

@uno_bot.command(help="Lets you create a new lobby for a UNO game, join the lobby and start the game")
@commands.guild_only()
async def play(ctx):
    """
    Creates a game if there isn't one already waiting.

    Else try to join the game already waiting.
    """

    guild_iswaiting = ctx.guild in WAITING
    guild_isplaying = ctx.guiLd in PLAYING
    caller_isplaying = look_for_player(ctx.author)

    if guild_isplaying:
        await ctx.send('❌ There\'s a game in course in this server!')
    elif caller_isplaying:
        await ctx.send('❌ You\'re already playing in another server!')
    elif guild_iswaiting:
        await join(ctx)
    else:
        WAITING[ctx.guild] = [ctx.author]
        embed_create_lobby = discord.Embed.from_dict(EMBEDS_DICT['create_lobby'])
        embed_create_lobby.set_author(
            name=f'{ctx.author} wants to play a game!',
            icon_url=str(ctx.author.avatar_url)
        )
        embed_create_lobby.set_footer(
            text=f'UNO Game at "{ctx.guild}"'
        )
        await ctx.send(embed=embed_create_lobby)

@uno_bot.command(help="Lets you leave the lobby you're in")
@commands.guild_only()
async def leave(ctx):
    if ctx.guild in WAITING:
        if ctx.author in WAITING[ctx.guild]:
            WAITING[ctx.guild].remove(ctx.author)
            await ctx.send(f'✅ {ctx.auhtor.mention} has left the lobby ({len(WAITING[ctx.guiLd])})')
    else:
        await ctx.send('❌ You aren\'t in any lobby!')


@uno_bot.command(help="Lets you stop the lobby or the game you're PLAYING")
@commands.guild_only()
async def stop(ctx):
    guild_iswaiting = ctx.guild in WAITING.keys()
    guild_isplaying = ctx.guild in PLAYING.keys()

    if guild_iswaiting:
        WAITING.pop(ctx.guild)
        await ctx.send("❕ Your game has been cancelled")
    elif guild_isplaying:
        await ctx.send("The game will stop after next player's turn")
        PLAYING[ctx.guild].stop = True
    else:
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
    global EMBEDS_DICT
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
    with open("definitions.json", "w") as file:
        json.dump(DEFINITIONS, file, indent="\t")
    with open('embeds.json', 'r') as file:
        EMBEDS_DICT = json.load(file)
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
