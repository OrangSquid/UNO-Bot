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

    def __init__(self, players, guild):
        self.guild = guild
        self.drawing_deck = random.shuffle(DECK)
        self.order = random.shuffle(players)
        self.on_table = self.drawing_deck.pop(0)
        validate = self.on_table.find
        while validate("wild") or validate("reverse") or validate("skip") or validate("plus"):
            self.drawing_deck.append(self.on_table)
            self.on_table = self.drawing_deck.pop(0)

        for player in self.order:
            for x in range(0, 6):
                player.deck.append(self.drawing_deck.pop(0))

    async def play_game(self):
        for player in self.order:
            await player.user.send()
        while len(self.order) != 1:
            for player in self.order:
                pass

class Player:

    def __init__(self, user):
        self.deck = []
        self.user = user
