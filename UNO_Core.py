import random

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

    def __init__(self, players, card_emojis, channel, bot):
        # Variables to be used later
        self.waiting_for = None       # The current player's turn
        self.playing_card = None      # Holds the card to be played temporarily for checking
        self.color_change = None      # Holds the color information for change if wild card is used
        self.skip = False             # Tells if next player's turn is skipped or not
        self.draw = 0                 # Tells how many cards the next player must draw
        self.played_cards = []
        self.CARD_EMOJIS = card_emojis
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

        for player in self.order:
            for x in range(0, 7):
                player.deck.append(self.drawing_deck.pop(0))

    async def play_game(self):
        await self.channel.send("The order is as follows: ")
        for player in self.order:
            await self.channel.send(player.user.mention)
            await player.user.send("This is your deck")
            await player.user.send(self.deck_to_emoji(player))
        await self.channel.send("Card on the table:")
        await self.channel.send(self.CARD_EMOJIS[self.on_table])
        pointer = 0
        while len(self.order) != 1:
            player = self.order[pointer]
            if self.skip:
                await self.channel.send("{.user.mention}'s turn is skipped!".format(player))
                self.skip = False
                continue
            if self.draw:
                await self.channel.senf("{.user.mention} drew {} cards and their turn is skipped".format(player, self.draw))
                for x in range(self.draw):
                    player.deck.append(self.drawing_deck.pop(0))
                self.draw = 0
                continue
            await self.channel.send("Your turn: {.user.mention}".format(player))
            self.waiting_for = player
            # Loop for the player's turn
            while True:
                await self.bot.wait_for("message", check=self.check_playing_card)
                # Makes the card on the table a list for easier checking with indexes
                list_on_table = self.on_table.split()
                # Check card sent in DMs:
                # Wild Card
                if self.playing_card.startswith("wild"):
                    player.deck.remove(self.playing_card)
                    await player.user.send("Choose your color (red, yellow, green, blue)")
                    await self.bot.wait_for("message", check=self.check_wild_card_color)
                    await self.channel.send("{.user.mention} played a:".format(player))
                    await self.channel.send(self.CARD_EMOJIS["{} {}".format(self.color_change, self.playing_card)])
                    self.on_table = "{} wild".format(self.color_change)
                    self.color_change = None
                    if self.playing_card.endswith("plus"):
                        self.draw = 4
                    self.playing_card = None
                # Normal Card
                elif self.playing_card.startswith(list_on_table[0]) or self.playing_card.endswith(list_on_table[1]):
                    player.deck.remove(self.playing_card)
                    await self.channel.send("{.user.mention} played a:".format(player))
                    await self.channel.send(self.CARD_EMOJIS[self.playing_card])
                    self.on_table = self.playing_card
                    # Skip Card
                    if self.playing_card.endswith("skip"):
                        self.skip = True
                    # 2+ Card
                    elif self.playing_card.endswith("plus"):
                        self.draw = 2
                    # Reverse Card
                    elif self.playing_card.endswith("reverse"):
                        self.order.reverse()
                        if len(self.order) == 2:
                            pointer -= 1
                        else:
                            pointer = abs(pointer - len(self.order))
                    self.played_cards.append(self.played_card)
                    self.playing_card = None
                # Draw a Card
                elif self.playing_card == "draw":
                    player.deck.append(self.drawing_deck.pop(0))
                    await self.channel.send("{.user.mention} drew a card".format(player))
                # Invalid Card
                else:
                    await player.user.send("That card cannot be played!")
                    continue
                await player.user.send(self.deck_to_emoji(player))
                break
            if pointer == len(self.order) - 1:
                pointer = 0
            else:
                pointer += 1

    async def played_card(self):
        pass

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
        for card in player.deck:
            to_send += str(self.CARD_EMOJIS[card])
        return to_send


class Player:

    def __init__(self, user):
        self.deck = []
        self.user = user
