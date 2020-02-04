import random
import discord
import datetime

DECK = ['wild card', 'wild card', 'wild card', 'wild card', 'wild plus', 'wild plus', 'wild plus', 'wild plus',
        'red 0', 'red 1', 'red 1', 'red 2', 'red 2', 'red 3', 'red 3', 'red 4', 'red 4', 'red 5', 'red 5', 'red 6',
        'red 6', 'red 7', 'red 7', 'red 8', 'red 8', 'red 9', 'red 9', 'red skip', 'red skip', 'red reverse',
        'red reverse', 'red plus', 'red plus', 'blue 0', 'blue 1', 'blue 1', 'blue 2', 'blue 2', 'blue 3', 'blue 3',
        'blue 4', 'blue 4', 'blue 5', 'blue 5', 'blue 6', 'blue 6', 'blue 7', 'blue 7', 'blue 8', 'blue 8', 'blue 9',
        'blue 9', 'blue skip', 'blue skip', 'blue reverse', 'blue reverse', 'blue plus', 'blue plus', 'yellow 0',
        'yellow 1', 'yellow 1', 'yellow 2', 'yellow 2', 'yellow 3', 'yellow 3', 'yellow 4', 'yellow 4', 'yellow 5',
        'yellow 5', 'yellow 6', 'yellow 6', 'yellow 7', 'yellow 7', 'yellow 8', 'yellow 8', 'yellow 9', 'yellow 9',
        'yellow skip', 'yellow skip', 'yellow reverse', 'yellow reverse', 'yellow plus', 'yellow plus', 'green 0',
        'green 1', 'green 1', 'green 2', 'green 2', 'green 3', 'green 3', 'green 4', 'green 4', 'green 5', 'green 5',
        'green 6', 'green 6', 'green 7', 'green 7', 'green 8', 'green 8', 'green 9', 'green 9', 'green skip',
        'green skip', 'green reverse', 'green reverse', 'green plus', 'green plus']


class Uno:

    def __init__(self, players, card_info, channel, bot):
        # Variables to be used later
        self.waiting_for = None  # The current player's turn
        self.playing_card = None  # Holds the card to be played temporarily for checking
        self.color_change = None  # Holds the color information for change if wild card is used
        self.pointer = 0
        self.played_cards = []
        self.COLOR_TO_DECIMAL = {
            "red": 16733525,
            "blue": 5592575,
            "green": 5614165,
            "yellow": 16755200
        }
        self.CARD_INFO = card_info
        self.channel = channel
        self.bot = bot
        self.drawing_deck = random.sample(DECK, k=len(DECK))
        self.order = random.sample(players, k=len(players))
        self.on_table = self.drawing_deck.pop(0)
        # Validation of the selected card on table
        # Wild, reverse, skip and +2 cards are invalid to start a game of UNO
        validate_back = self.on_table.endswith
        validate_front = self.on_table.startswith
        while validate_front("wild") or validate_back("reverse") or validate_back("skip") or validate_back("plus"):
            self.drawing_deck.append(self.on_table)
            self.on_table = self.drawing_deck.pop(0)
            validate_back = self.on_table.endswith
            validate_front = self.on_table.startswith

        for player in self.order:
            for x in range(0, 7):
                player.deck.append(self.drawing_deck.pop(0))

    async def play_game(self):
        embed_order = discord.Embed(title="The game order will be: ", description="", timestamp=datetime.datetime.now())
        embed_order.set_author(name="Let's Play!", icon_url=str(self.bot.get_user(671451098820640769).avatar_url))
        embed_order.set_footer(text="UNO Game at \"{}\"".format(self.channel.guild))
        first = True
        for player in self.order:
            if first:
                embed_order.set_thumbnail(url=str(player.user.avatar_url))
            embed_order.description += str(player.user) + "\n"
            first = False
        await self.channel.send(embed=embed_order)

        embed_on_table = discord.Embed(color=self.COLOR_TO_DECIMAL[self.on_table.split()[0]],
                                       timestamp=datetime.datetime.now())
        embed_on_table.set_author(name="First Turn", icon_url=str(self.bot.get_user(671451098820640769).avatar_url))
        embed_on_table.description = "The card on the table is a {}\nYour turn now **{}**".format(
            self.CARD_INFO[self.on_table][0], self.order[0].user)
        embed_on_table.set_thumbnail(url=self.CARD_INFO[self.on_table][2])
        embed_on_table.timestamp = datetime.datetime.now()
        embed_on_table.set_footer(text="UNO game at \"{}\"".format(self.channel.guild))
        await self.channel.send(embed=embed_on_table)

        for player in self.order:
            await player.user.send(self.deck_to_emoji(player))

        drew_card = False
        while len(self.order) != 1:
            player = self.order[self.pointer]
            embed_turn = discord.Embed(description="")
            embed_turn.set_author(name="{} turn".format(player.user), icon_url=str(player.user.avatar_url))
            embed_turn.set_footer(text="UNO game at \"{}\"".format(self.channel.guild))

            if drew_card:
                embed_turn.description += "{} drew a card\n".format(player.user)

            # await self.channel.send("Your turn: {.user.mention}".format(player))
            self.waiting_for = player
            # Waits for the message from the player, the check function also changes self.playing_card
            await self.bot.wait_for("message", check=self.check_playing_card)
            # Makes the card on the table a list for easier checking with indexes
            list_on_table = self.on_table.split()

            # Check card sent in DMs:

            # Wild Card
            if self.playing_card.startswith("wild"):
                embed_turn = await self.played_card(player, True, embed_turn)

            # Normal Card
            elif self.playing_card.startswith(list_on_table[0]) or self.playing_card.endswith(list_on_table[1]):
                embed_turn = await self.played_card(player, False, embed_turn)
                # Skip Card
                if self.playing_card.endswith("skip"):
                    self.pointer = self.increment_pointer(self.pointer)
                    embed_turn.description += "\n{} turn is skipped".format(self.order[self.pointer].user)
                # 2+ Card
                elif self.playing_card.endswith("plus"):
                    embed_turn = self.draw_card(embed_turn, 2)
                # Reverse Card
                elif self.playing_card.endswith("reverse"):
                    if len(self.order) == 2:
                        self.pointer -= 1
                    else:
                        self.order.reverse()
                        self.pointer = abs(self.pointer - len(self.order))
                    embed_turn.description += "\nThe order has been reversed"

            # Draw a Card
            elif self.playing_card == "draw":
                drawn_card = self.drawing_deck.pop(0)
                player.deck.append(drawn_card)
                if drawn_card.startswith(list_on_table[0]) or drawn_card.endswith(list_on_table[1]) or drawn_card.startswith("wild"):
                    await player.user.send("You can play the card you drew!")
                    await player.user.send(self.deck_to_emoji(player))
                    drew_card = True
                    continue
                else:
                    embed_turn.description += "{} drew a card".format(player.user)
                    embed_turn.set_thumbnail(url="https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck"
                                                 "/card%20draw.png")

            # Invalid Card
            else:
                await player.user.send("That card cannot be played!")
                continue

            await player.user.send(self.deck_to_emoji(player))
            if not player.deck:
                self.order.remove(player)
                await self.channel.send("{.user.mention} has no cards! They are leaving the game!".format(player))

            self.pointer = self.increment_pointer(self.pointer)
            embed_turn.description += "\nYour turn now, **{}**".format(self.order[self.pointer].user)
            embed_turn.timestamp = datetime.datetime.now()
            if self.playing_card != "draw":
                embed_turn.color = self.COLOR_TO_DECIMAL[self.playing_card.split()[0]]
            drew_card = False
            await self.channel.send(embed=embed_turn)

        else:
            await self.channel.send("The game has ended!")

    async def played_card(self, player, is_wild, embed):
        player.deck.remove(self.playing_card)
        if is_wild:
            await player.user.send("Choose your color (red, yellow, green, blue)")
            # Waits for the message and self.color_change is also changed in the check function
            await self.bot.wait_for("message", check=self.check_wild_card_color)
            if self.playing_card.endswith("plus"):
                embed = self.draw_card(embed, 4)
            self.playing_card = "{} {}".format(self.color_change, self.playing_card)
            self.on_table = "{} wild".format(self.color_change)
            self.color_change = None
        else:
            self.on_table = self.playing_card
        embed.description += "{.user} played a {}".format(player, self.CARD_INFO[self.playing_card][0])
        embed.set_thumbnail(url=self.CARD_INFO[self.playing_card][2])
        self.played_cards.append(self.playing_card)
        return embed

    def draw_card(self, embed, cards_to_draw):
        temp_pointer = self.increment_pointer(self.pointer)
        for x in range(cards_to_draw):
            self.order[temp_pointer].deck.append(self.drawing_deck.pop(0))
        embed.description += "\n{} drew {} and their turn is skipped".format(self.order[temp_pointer].user,
                                                                             cards_to_draw)
        self.pointer = temp_pointer
        return embed

    def increment_pointer(self, pointer: int) -> int:
        return_pointer = pointer
        if pointer >= len(self.order) - 1:
            return_pointer = 0
            return return_pointer
        else:
            return_pointer += 1
            return return_pointer

    def check_playing_card(self, message):
        content = message.content
        if (message.author == self.waiting_for.user) and (content in self.waiting_for.deck or content == "draw"):
            self.playing_card = content
            return True

    def check_wild_card_color(self, message):
        colors = ["red", "yellow", "green", "blue"]
        if message.author == self.waiting_for.user and message.content in colors:
            self.color_change = message.content
            return True

    def deck_to_emoji(self, player):
        to_send = ""
        if not player.deck:
            return "Your deck is empty"
        else:
            for card in player.deck:
                to_send += str(self.CARD_INFO[card][1])
            return to_send


class Player:

    def __init__(self, user):
        self.deck = []
        self.user = user
