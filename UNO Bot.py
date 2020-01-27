import discord
import logging
from discord.ext import commands

unob = commands.Bot(command_prefix = "!")

# Setting up the logger function for the library
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('[%(asctime)s]: %(levelname)s: %(name)s: %(message)s'))
logger.addHandler(handler)

@unob.command()
async def play_uno(ctx):
	await ctx.send("{user} wants to start a game!".format(user = ctx.author))

@unob.command()
async def settings(ctx):
	pass

@unob.event
async def on_ready():
	print("We are ready to roll!")

def main():
	with open("Token.txt", "r") as token:
		unob.run(token.read())

if __name__ == "__main__":
	main()