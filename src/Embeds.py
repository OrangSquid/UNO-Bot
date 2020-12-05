import datetime
import discord

def embed_order(player_list) -> discord.Embed:
    embed = discord.Embed(title='The game order will be:', timestamp=datetime.datetime.now())
    embed.set_author(name='Let\'s Play!', icon_url='https://cdn.discordapp.com/avatars/671451098820640769/455191e488b794a1d7b5b4a891ef2165.webp?size=1024')
    embed.set_thumbnail(url=player_list[0].avatar_url)
    embed.description = str(player_list[0])
    for player in player_list:
        embed.description += "\n" + str(player)
    embed.description += '\n*To play your cards in your DMs with the bot or in this channel use: ' \
                         '\n"color (red, yellow, green, blue, wild)\n (space) \nsymbol/number(skip, ' \
                         'reverse, plus, 0, 1, ...)"*\n**To use a wild card, just use "wild card"\nTo ' \
                         'use a wild 4+, just use "wild plus"** '
    
    return embed

def embed_on_table(card, player) -> discord.Embed:
    embed = discord.Embed(color=card.color, timestamp=datetime.datetime.now())
    embed.set_author(name='First Turn', icon_url='https://cdn.discordapp.com/avatars/671451098820640769/455191e488b794a1d7b5b4a891ef2165.webp?size=1024')
    embed.description = f'The card on the table is a {card}\nYour turn now **{player}**'
    embed.description = player.deck_back
    embed.set_thumbnail(url=card.image_url)
    embed.timestamp = datetime.datetime.now()

    return embed