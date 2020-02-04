import logging
import uno_core
import discord
import datetime
from discord.ext import commands

# Setting up the logger function for the library
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('[%(asctime)s]: %(levelname)s: %(name)s: %(message)s'))
logger.addHandler(handler)


# TODO: add a way to change the command prefix (maybe?)
async def prefix(bot, message):
    return "uno "


# Global variables to keep track of games and who's waiting
waiting = {}
playing = {}
CARD_INFO = {}
uno_bot = commands.Bot(command_prefix=prefix)


async def look_for_player(caller):
    # Looks if the caller of either join or play_uno is already in a game to avoid confusion in DMs with the bot
    for game in playing.values():
        for player in game:
            if player == caller:
                return True
    for lobby in waiting.values():
        for player in lobby:
            if player == caller:
                return True
    else:
        return False


@uno_bot.command()
async def play(ctx):
    # Checks if there's already a game waiting to start
    # If not, make a new one
    try:
        print(waiting[ctx.guild])
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
            embed_to_send.set_thumbnail(url="https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/logo.png")
            embed_to_send.set_footer(text="UNO Game at \"{.guild}\"".format(ctx))
            await ctx.send(embed=embed_to_send)
    else:
        await ctx.send(":x: There's already a game waiting to start or one is already on course")


@uno_bot.command()
async def join(ctx):
    try:
        if ctx.author in waiting[ctx.guild]:
            await ctx.send(":x: You are already waiting for the game")
        elif await look_for_player(ctx.author):
            await ctx.send(":x: You are already in a game in this or in another server!")
        else:
            waiting[ctx.guild].append(ctx.author)
            await ctx.send(
                ":white_check_mark: {} has joined the game ({}/6)".format(ctx.author.mention, len(waiting[ctx.guild])))
    except KeyError:
        await ctx.send(":x: There are no current games waiting to start")


@uno_bot.command()
async def start(ctx):
    try:
        if len(waiting[ctx.guild]) == 1:
            await ctx.send(":grey_exclamation: There aren't enough players to start. You need at least 2.")
        else:
            players = []
            for player in waiting[ctx.guild]:
                players.append(uno_core.Player(player))
            game = uno_core.Uno(players, CARD_INFO, ctx.channel, uno_bot)
            playing[ctx.guild] = waiting[ctx.guild]
            waiting.pop(ctx.guild)
            await game.play_game()
            print("the fuck")
            playing.pop(ctx.guild)
    except KeyError:
        await ctx.send(":x: There's no game to start!")


@uno_bot.command()
async def exit_waiting(ctx):
    pass


@uno_bot.command()
async def stop_waiting(ctx):
    try:
        waiting.pop(ctx.guild)
        await ctx.send(":grey_exclamation: Your game has been cancelled")
    except KeyError:
        await ctx.send(":x: There are no games to stop")


@uno_bot.command()
async def settings(ctx):
    pass


@uno_bot.event
async def on_ready():
    global CARD_INFO
    CARD_INFO = {"red 0": ["**RED 0**", uno_bot.get_emoji(672954923008131122),
                           "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/red%200.png"],
                 "red 1": ["**RED 1**", uno_bot.get_emoji(672954938409615383),
                           "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/red%201.png"],
                 "red 2": ["**RED 2**", uno_bot.get_emoji(672955019666128946),
                           "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/red%202.png"],
                 "red 3": ["**RED 3**", uno_bot.get_emoji(672955040058834954),
                           "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/red%203.png"],
                 "red 4": ["**RED 4**", uno_bot.get_emoji(672955053639991337),
                           "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/red%204.png"],
                 "red 5": ["**RED 5**", uno_bot.get_emoji(672955063106404411),
                           "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/red%205.png"],
                 "red 6": ["**RED 6**", uno_bot.get_emoji(672955071000215553),
                           "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/red%206.png"],
                 "red 7": ["**RED 7**", uno_bot.get_emoji(672955078142853141),
                           "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/red%207.png"],
                 "red 8": ["**RED 8**", uno_bot.get_emoji(672955085919092748),
                           "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/red%208.png"],
                 "red 9": ["**RED 9**", uno_bot.get_emoji(672955093489811467),
                           "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/red%209.png"],
                 "red plus": ["**RED 2+**", uno_bot.get_emoji(672955105590509595),
                              "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/red%20plus.png"],
                 "red reverse": ["**RED REVERSE**", uno_bot.get_emoji(672955116407619595),
                                 "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/red%20reverse.png"],
                 "red skip": ["**RED SKIP**", uno_bot.get_emoji(672955128281563146),
                              "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/red%20skip.png"],
                 "yellow 0": ["**YELLOW 0**", uno_bot.get_emoji(672955142232080404),
                              "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/yellow%200.png"],
                 "yellow 1": ["**YELLOW 1**", uno_bot.get_emoji(672955153032282122),
                              "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/yellow%201.png"],
                 "yellow 2": ["**YELLOW 2**", uno_bot.get_emoji(672955162494500864),
                              "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/yellow%202.png"],
                 "yellow 3": ["**YELLOW 3**", uno_bot.get_emoji(672955172355440651),
                              "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/yellow%203.png"],
                 "yellow 4": ["**YELLOW 4**", uno_bot.get_emoji(672955181729579008),
                              "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/yellow%204.png"],
                 "yellow 5": ["**YELLOW 5**", uno_bot.get_emoji(672955193968820235),
                              "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/yellow%205.png"],
                 "yellow 6": ["**YELLOW 6**", uno_bot.get_emoji(672955205025005572),
                              "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/yellow%206.png"],
                 "yellow 7": ["**YELLOW 7**", uno_bot.get_emoji(672955215166701598),
                              "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/yellow%207.png"],
                 "yellow 8": ["**YELLOW 8**", uno_bot.get_emoji(672955225396477973),
                              "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/yellow%208.png"],
                 "yellow 9": ["**YELLOW 9**", uno_bot.get_emoji(672955235005759508),
                              "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/yellow%209.png"],
                 "yellow plus": ["**YELLOW 2+**", uno_bot.get_emoji(672955248784179208),
                                 "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/yellow%20plus.png"],
                 "yellow reverse": ["**YELLOW REVERSE**", uno_bot.get_emoji(672955258598850589),
                                    "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/yellow"
                                    "%20reverse.png"],
                 "yellow skip": ["**YELLOW SKIP**", uno_bot.get_emoji(672955269512167454),
                                 "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/yellow%20skip.png"],
                 "green 0": ["**GREEN 0**", uno_bot.get_emoji(672955280916611084),
                             "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/green%200.png"],
                 "green 1": ["**GREEN 1**", uno_bot.get_emoji(672955290123239445),
                             "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/green%201.png"],
                 "green 2": ["**GREEN 2**", uno_bot.get_emoji(672955297974714369),
                             "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/green%202.png"],
                 "green 3": ["**GREEN 3**", uno_bot.get_emoji(672955305839296562),
                             "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/green%203.png"],
                 "green 4": ["**GREEN 4**", uno_bot.get_emoji(672955311648276500),
                             "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/green%204.png"],
                 "green 5": ["**GREEN 5**", uno_bot.get_emoji(672955324864528385),
                             "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/green%205.png"],
                 "green 6": ["**GREEN 6**", uno_bot.get_emoji(672955334033276960),
                             "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/green%206.png"],
                 "green 7": ["**GREEN 7**", uno_bot.get_emoji(672955343843622923),
                             "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/green%207.png"],
                 "green 8": ["**GREEN 8**", uno_bot.get_emoji(672955351926177812),
                             "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/green%208.png"],
                 "green 9": ["**GREEN 9**", uno_bot.get_emoji(672955360570638369),
                             "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/green%209.png"],
                 "green plus": ["**GREEN 2+**", uno_bot.get_emoji(672955374319566877),
                                "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/green%20plus.png"],
                 "green reverse": ["**GREEN REVERSE**", uno_bot.get_emoji(672955383999889448),
                                   "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/green%20reverse"
                                   ".png"],
                 "green skip": ["**GREEN SKIP**", uno_bot.get_emoji(672955391277137931),
                                "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/green%20skip.png"],
                 "blue 0": ["**BLUE 0**", uno_bot.get_emoji(672955401897246721),
                            "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/blue%200.png"],
                 "blue 1": ["**BLUE 1**", uno_bot.get_emoji(672955411887816714),
                            "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/blue%201.png"],
                 "blue 2": ["**BLUE 2**", uno_bot.get_emoji(672955419764719626),
                            "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/blue%202.png"],
                 "blue 3": ["**BLUE 3**", uno_bot.get_emoji(672955428727947284),
                            "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/blue%203.png"],
                 "blue 4": ["**BLUE 4**", uno_bot.get_emoji(672955436139544640),
                            "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/blue%204.png"],
                 "blue 5": ["**BLUE 5**", uno_bot.get_emoji(672955445169881138),
                            "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/blue%205.png"],
                 "blue 6": ["**BLUE 6**", uno_bot.get_emoji(672955453335928870),
                            "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/blue%206.png"],
                 "blue 7": ["**BLUE 7**", uno_bot.get_emoji(672955460701388830),
                            "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/blue%207.png"],
                 "blue 8": ["**BLUE 8**", uno_bot.get_emoji(672955468284559380),
                            "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/blue%208.png"],
                 "blue 9": ["**BLUE 9**", uno_bot.get_emoji(672955477063237653),
                            "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/blue%209.png"],
                 "blue plus": ["**BLUE 2+**", uno_bot.get_emoji(672955485066100746),
                               "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/blue%20plus.png"],
                 "blue reverse": ["**BLUE REVERSE**", uno_bot.get_emoji(672955984477552653),
                                  "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/blue%20"
                                  "reverse.png"],
                 "blue skip": ["**BLUE SKIP**", uno_bot.get_emoji(672955996041248780),
                               "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/blue%20skip.png"],
                 "wild card": ["**WILD CARD**", uno_bot.get_emoji(672956006158041126),
                               "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/wild%20card.png"],
                 "wild plus": ["**WILD 4+**", uno_bot.get_emoji(672956016542875681),
                               "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/wild%20plus.png"],
                 "red wild card": ["**RED WILD CARD**", uno_bot.get_emoji(673909975764041749),
                                   "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/red%20wild"
                                   "%20card.png"],
                 "red wild plus": ["**RED WILD 4+**", uno_bot.get_emoji(673909988846206976),
                                   "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/red%20wild"
                                   "%20plus.png"],
                 "yellow wild card": ["**YELLOW WILD CARD**", uno_bot.get_emoji(673910001475125250),
                                      "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/yellow%20wild"
                                      "%20card.png"],
                 "yellow wild plus": ["**YELLOW WILD 4+**", uno_bot.get_emoji(673910013437149194),
                                      "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/yellow%20wild"
                                      "%20plus.png"],
                 "green wild card": ["**GREEN WILD CARD**", uno_bot.get_emoji(673909955375398928),
                                     "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/green%20wild"
                                     "%20card.png"],
                 "green wild plus": ["**GREEN WILD 4+**", uno_bot.get_emoji(673909964263391243),
                                     "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/green%20wild"
                                     "%20plus.png"],
                 "blue wild card": ["**BLUE WILD CARD**", uno_bot.get_emoji(673909927131217971),
                                    "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/blue%20wild"
                                    "%20card.png"],
                 "blue wild plus": ["**BLUE WILD 4+**", uno_bot.get_emoji(673909940867301377),
                                    "https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck/blue%20wild"
                                    "%20plus.png"]
                 }
    print("We are ready to roll!")


def main():
    with open("Token.txt", "r") as token:
        uno_bot.run(token.read())


if __name__ == "__main__":
    main()
