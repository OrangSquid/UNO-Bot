import discord
import logging
import UNO_Core
import json
from discord.ext import commands

unob = commands.Bot(command_prefix = "!")

# Setting up the logger function for the library
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('[%(asctime)s]: %(levelname)s: %(name)s: %(message)s'))
logger.addHandler(handler)

CURRENT_GAMES = {}
WAITING = {}

@unob.command()
async def play_uno(ctx):
	WAITING[ctx.guild] = [ctx.author]
	print(WAITING)
	await ctx.send("{user} wants to start a game!".format(user = ctx.author.mention))
	await ctx.send("If anybody wants to join the game, please use !join")
	await ctx.send("Up to 6 players can join")

@unob.command()
async def join(ctx):
	try:
		if ctx.author in WAITING[ctx.guild]:
			await ctx.send("You are already waiting for the game")
		else:
			WAITING[ctx.guild].append(ctx.author)
	except KeyError:
		await ctx.send("There are no current games waiting to start")

@unob.command()
async def start(ctx):
	pass

@unob.command()
async def stop(ctx):
	pass

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