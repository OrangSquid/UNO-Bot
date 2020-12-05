import json
import logging
from typing import Any, Dict, List

import discord
import UNO_Core
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
    return 'uno '

# Global variables to keep track of games and who's WAITING
waiting: Dict[int, List[discord.User]] = {}
playing: Dict[int, UNO_Core.Uno] = {}
# Keep track of settinfs and card info like the emojis and images
settings: Dict[Any, Any] = {}
uno_bot = commands.Bot(command_prefix=prefix)
EMBEDS_DICT = {}


def look_for_player(caller: discord.User) -> bool:
    """
    Looks if the caller of either join or play_uno is already in a game to avoid confusion in DMs with the bot
    """
    return any(caller in lobby for lobby in waiting.values()) or any(caller in game for game in playing.values())

async def join(ctx):
    """
    Tries to join the game waiting.

    Else try to start it
    """

    wait_list = waiting[ctx.guild.id]
    if ctx.author not in wait_list and len(wait_list) < 6:
        waiting[ctx.guild.id].append(ctx.author)
        await ctx.send(f'✅ {ctx.author.mention} has joined the game ({len(wait_list)}/6)')
    elif ctx.author == wait_list[0]:
        await start(ctx)
    else:
        await ctx.send('❌ You\'re already in the game or the lobby is full!\n❕ Please note the first caller of the play command should call it again to begin the game')

async def start(ctx):
    """
    Starts the game provided there's one in WAITING
    """

    wait_list = waiting[ctx.guild.id]
    if len(wait_list) == 1:
        await ctx.send('❕ There aren\'t enough players to start. You need at least 2.')
    else:
        players = [UNO_Core.Player(player) for player in wait_list]
        game = UNO_Core.Uno(players, settings[str(
            ctx.guild.id)], CARD_INFO, ctx.channel, uno_bot)
        playing[ctx.guild.id] = game
        del waiting[ctx.guild.id]
        await game_loop(game)
        del playing[ctx.guild.id]

@uno_bot.command(help="Lets you create a new lobby for a UNO game, join the lobby and start the game")
@commands.guild_only()
async def play(ctx):
    """
    Creates a game if there isn't one already waiting.

    Else try to join the game already waiting.
    """

    guild_iswaiting = ctx.guild.id in waiting
    guild_isplaying = ctx.guild.id in playing
    caller_isplaying = look_for_player(ctx.author)

    if guild_isplaying:
        await ctx.send('❌ There\'s a game in course in this server!')
    elif caller_isplaying:
        if guild_iswaiting:
            if waiting[ctx.guild.id][0] == ctx.author:
                await join(ctx)
        else:
            await ctx.send('❌ You\'re already playing in another server!')
    elif guild_iswaiting:
        await join(ctx)
    else:
        waiting[ctx.guild.id] = [ctx.author]
        embed_create_lobby = discord.Embed.from_dict(EMBEDS_DICT['create_lobby'])
        embed_create_lobby.set_author(
            name=f'{ctx.author} wants to play a game!',
            icon_url=str(ctx.author.avatar_url)
        )
        embed_create_lobby.set_footer(
            text=f'UNO Game at "{ctx.guild}"'
        )
        await ctx.send(embed=embed_create_lobby)

async def game_loop(ctx, game):
    for action in game.action_relay():
        if isinstance(action, discord.Embed):
            await ctx.send(embed=action)
        elif action in ['wait_card', 'wait_color']:
            message = await uno_bot.wait_for('message', check=lambda x: True)
            if action == 'wait_card':
                game.playing_card = message
            else:
                game.color_change = message
        else:
            await ctx.send(action)

@uno_bot.command(help="Lets you leave the lobby you're in")
@commands.guild_only()
async def leave(ctx):
    if ctx.guild.id in waiting:
        if ctx.author in waiting[ctx.guild.id]:
            waiting[ctx.guild.id].remove(ctx.author)
            await ctx.send(f'✅ {ctx.auhtor.mention} has left the lobby ({len(waiting[ctx.guild.id])})')
    else:
        await ctx.send('❌ You aren\'t in any lobby!')


@uno_bot.command(help="Lets you stop the lobby or the game you're PLAYING")
@commands.guild_only()
async def stop(ctx):
    guild_iswaiting = ctx.guild.id in waiting.keys()
    guild_isplaying = ctx.guild.id in playing.keys()

    if guild_iswaiting:
        waiting.pop(ctx.guild.id)
        await ctx.send("❕ Your game has been cancelled")
    elif guild_isplaying:
        await ctx.send("The game will stop after next player's turn")
        playing[ctx.guild.id].stop = True
    else:
        await ctx.send(":x: There are no games to stop")


@uno_bot.group()
async def settings(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send(":x: Choose a setting! Please use uno help to get a full list of settings")


@settings.command()
async def decks(ctx, number: int):
    await change_settings('decks', number, ctx.guild.id)
    await ctx.send(f'The number of decks has changed to {number}')


@settings.command()
async def initial_cards(ctx, number: int):
    await change_settings("initial_cards", number, ctx.guild.id)
    await ctx.send(f'The number of initial cards to give to each player has changed to {number}')


@settings.command()
async def draw_skip(ctx, change: bool):
    await change_settings("draw_skip", change, ctx.guild.id)
    message = 'You must now skip after a 2+ or 4+ card' if change else 'You can now play after a 2+ or 4+ card'
    await ctx.send(message)


@settings.command()
async def must_play(ctx, change: bool):
    await change_settings("must_play", change, ctx.guild.id)
    message = 'You can now play after drawing a card you can play' if change else 'You must now skip a turn after drawing a card'
    await ctx.send(message)


@settings.command()
async def stacking(ctx, change: bool):
    await change_settings("stacking", change, ctx.guild.id)
    message = 'You can now stack 2+\'s' if change else 'You can\'t stack 2+\'s'
    await ctx.send(message)


async def change_settings(setting: str, to_change, guild_id: int):
    settings[str(guild_id)][setting] = to_change
    with open("settings.json", "w") as file:
        json.dump(settings, file, indent="\t")


@uno_bot.event
async def on_guild_join(guild):
    settings[guild.id] = settings["default"]
    with open("settinfs.json.json", "w") as file:
        json.dump(settings, file, indent="\t")


@uno_bot.event
async def on_ready():
    #global settings
    #global CARD_INFO
    global EMBEDS_DICT
    # Loading the card info file
    """with open("info.json", "r") as file:
        CARD_INFO = json.load(file)
        for x in zip(CARD_INFO.keys(), CARD_INFO.values()):
            CARD_INFO[x[0]][1] = uno_bot.get_emoji(x[1][1])"""
    # Loading the settinfs file and filling in any guild missing
    """with open("settings.json", "r") as file:
        settings = json.load(file)
        for guild in uno_bot.guilds:
            if str(guild.id) not in settings:
                settings[guild.id] = settings["default"]
    with open("settings.json", "w") as file:
        json.dump(settings, file, indent="\t")"""
    with open('json/embeds.json', 'r') as file:
        EMBEDS_DICT = json.load(file)
    print("We are ready to roll!")


def main():
    with open("Token.txt", "r") as token:
        uno_bot.run(token.read())


if __name__ == '__main__':
    main()
