import logging
import UNO_Core
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
waiting = {}
playing = {}
CARD_EMOJIS = {}
uno_bot = commands.Bot(command_prefix=prefix)


@uno_bot.command()
async def play_uno(ctx):
    # Checks if there's already a game waiting to start
    # If not, make a new one
    try:
        waiting[ctx.guild]
    except KeyError:
        waiting[ctx.guild] = [ctx.author]
        await ctx.send("{user} wants to start a game!".format(user=ctx.author.mention))
        await ctx.send("If anybody wants to join the game, use !join")
        await ctx.send("Up to 6 players can join")
    else:
        await ctx.send("There's already a game waiting to start")


@uno_bot.command()
async def join(ctx):
    try:
        if ctx.author in waiting[ctx.guild]:
            await ctx.send("You are already waiting for the game")
        else:
            waiting[ctx.guild].append(ctx.author)
            await ctx.send("{} has joined the game".format(ctx.author.mention))
    except KeyError:
        await ctx.send("There are no current games waiting to start")


@uno_bot.command()
async def start(ctx):
    if len(waiting[ctx.guild]) == 1:
        return
    else:
        players = []
        try:
            for player in waiting[ctx.guild]:
                players.append(UNO_Core.Player(player))
            game = UNO_Core.Uno(players, CARD_EMOJIS, ctx.channel, uno_bot)
            await ctx.send("Let's play")
            playing[ctx.guild] = game
            await game.play_game()
            playing.pop(ctx.guild)
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
    global CARD_EMOJIS
    CARD_EMOJIS = {"red 0": uno_bot.get_emoji(672954923008131122),
                   "red 1": uno_bot.get_emoji(672954938409615383),
                   "red 2": uno_bot.get_emoji(672955019666128946),
                   "red 3": uno_bot.get_emoji(672955040058834954),
                   "red 4": uno_bot.get_emoji(672955053639991337),
                   "red 5": uno_bot.get_emoji(672955063106404411),
                   "red 6": uno_bot.get_emoji(672955071000215553),
                   "red 7": uno_bot.get_emoji(672955078142853141),
                   "red 8": uno_bot.get_emoji(672955085919092748),
                   "red 9": uno_bot.get_emoji(672955093489811467),
                   "red plus": uno_bot.get_emoji(672955105590509595),
                   "red reverse": uno_bot.get_emoji(672955116407619595),
                   "red skip": uno_bot.get_emoji(672955128281563146),
                   "yellow 0": uno_bot.get_emoji(672955142232080404),
                   "yellow 1": uno_bot.get_emoji(672955153032282122),
                   "yellow 2": uno_bot.get_emoji(672955162494500864),
                   "yellow 3": uno_bot.get_emoji(672955172355440651),
                   "yellow 4": uno_bot.get_emoji(672955181729579008),
                   "yellow 5": uno_bot.get_emoji(672955193968820235),
                   "yellow 6": uno_bot.get_emoji(672955205025005572),
                   "yellow 7": uno_bot.get_emoji(672955215166701598),
                   "yellow 8": uno_bot.get_emoji(672955225396477973),
                   "yellow 9": uno_bot.get_emoji(672955235005759508),
                   "yellow plus": uno_bot.get_emoji(672955248784179208),
                   "yellow reverse": uno_bot.get_emoji(672955258598850589),
                   "yellow skip": uno_bot.get_emoji(672955269512167454),
                   "green 0": uno_bot.get_emoji(672955280916611084),
                   "green 1": uno_bot.get_emoji(672955290123239445),
                   "green 2": uno_bot.get_emoji(672955297974714369),
                   "green 3": uno_bot.get_emoji(672955305839296562),
                   "green 4": uno_bot.get_emoji(672955311648276500),
                   "green 5": uno_bot.get_emoji(672955324864528385),
                   "green 6": uno_bot.get_emoji(672955334033276960),
                   "green 7": uno_bot.get_emoji(672955343843622923),
                   "green 8": uno_bot.get_emoji(672955351926177812),
                   "green 9": uno_bot.get_emoji(672955360570638369),
                   "green plus": uno_bot.get_emoji(672955374319566877),
                   "green reverse": uno_bot.get_emoji(672955383999889448),
                   "green skip": uno_bot.get_emoji(672955391277137931),
                   "blue 0": uno_bot.get_emoji(672955401897246721),
                   "blue 1": uno_bot.get_emoji(672955411887816714),
                   "blue 2": uno_bot.get_emoji(672955419764719626),
                   "blue 3": uno_bot.get_emoji(672955428727947284),
                   "blue 4": uno_bot.get_emoji(672955436139544640),
                   "blue 5": uno_bot.get_emoji(672955445169881138),
                   "blue 6": uno_bot.get_emoji(672955453335928870),
                   "blue 7": uno_bot.get_emoji(672955460701388830),
                   "blue 8": uno_bot.get_emoji(672955468284559380),
                   "blue 9": uno_bot.get_emoji(672955477063237653),
                   "blue plus": uno_bot.get_emoji(672955485066100746),
                   "blue reverse": uno_bot.get_emoji(672955984477552653),
                   "blue skip": uno_bot.get_emoji(672955996041248780),
                   "wild card": uno_bot.get_emoji(672956006158041126),
                   "wild plus": uno_bot.get_emoji(672956016542875681),
                   "red wild card": uno_bot.get_emoji(673909975764041749),
                   "red wild plus": uno_bot.get_emoji(673909988846206976),
                   "yellow wild card": uno_bot.get_emoji(673910001475125250),
                   "yellow wild plus": uno_bot.get_emoji(673910013437149194),
                   "green wild card": uno_bot.get_emoji(673909955375398928),
                   "green wild plus": uno_bot.get_emoji(673909964263391243),
                   "blue wild card": uno_bot.get_emoji(673909927131217971),
                   "blue wild plus": uno_bot.get_emoji(673909940867301377)
                   }
    print("We are ready to roll!")


def main():
    with open("Token.txt", "r") as token:
        uno_bot.run(token.read())


if __name__ == "__main__":
    main()
