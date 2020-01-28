import random
import discord

DECK = ["red 0",
		"red 1",
		"red 1"]

class Uno():
	
	def __init__(self, players):
		self.drawing_deck = []
		self.order = random.shuffle(players)

	def play_game(self):
		pass

class Player():
	
	def __init__(self, user):
		self.deck = []
		self.user = user

class Card():

	def __init__(self, number, color):
		self.number = number
		self.color = color