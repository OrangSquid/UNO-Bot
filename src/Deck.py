from . import Card
import random

class Deck:

    def __init__(self, dict_cards):
        self.deck = [Card.Card(card) * times for card, times in dict_cards.items()]
        self.deck.shuffle()
        self.played_deck = []
    
    def draw(self, number):
        if len(self.deck) < number:
            self.deck = random.sample(self.played_deck, k=len(self.played_deck))
        return [self.deck.pop(index) for index in range(number)]
        