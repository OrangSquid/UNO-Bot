import random
import discord
import datetime
from src import Embeds, Player, Deck, Card
from typing import Dict, List, Any


class Uno:

    def __init__(self, players: List[Player], settings: Dict[str, List[Any]]):
        self.waiting_for = None            # The current player's turn
        # Holds the card to be played temporarily for checking
        self.playing_card = None
        # Holds the color information for change if wild card is used
        self.color_change = None
        self.reverse = False
        self.cards_to_draw = 0             # How many cards the next player must draw
        # Played cards to put back into the drawing deck when it runs out of cards
        self.settings = settings
        self.deck = Deck.Deck(settings['decks'])
        self.order = random.sample(players, k=len(players))
        self.on_table = self.drawing_deck.pop(0)
        # Validation of the selected card on table
        # Wild, reverse, skip and +2 cards are invalid to start a game of UNO
        while self.on_table.startswith('wild') or self.on_table.endswith('reverse') or self.on_table.endswith('skip') or self.on_table.endswith('plus'):
            self.drawing_deck.append(self.on_table)
            self.on_table = self.drawing_deck.pop(0)
            print(self.on_table)

        for player in self.order:
            player.deck = self.deck.draw(self.settings['initial_cards'])
    
    def __getitem__(self, index):
        return self.order[index]
    
    def __len__(self):
        return len(self.order)
    
    def __iter__(self):
        self._pointer = 0
        return self

    def __next__(self):
        self._pointer += 1 if self.reverse else self._pointer - 1
        if self._pointer >= len(self) and not self.reverse:
            self._pointer = 0
        else:
            self._pointer = len(self) - 1
        return self[self._pointer]

    async def action_relay(self) -> Any:
        yield Embeds.embed_order(self.order)
        yield Embeds.embed_on_table(self.on_table)

        # Send the cards at the beginning to each player
        for player in self.order:
            player.deck_emoji()

        # The loop for turns
        for player in self:
            self.waiting_for = player
            embed_turn = discord.Embed(description='')
            embed_turn.set_author(name=f'{player} turn', icon_url=str(player.avatar_url))

            # Waits for the message from the player, the check function also changes self.playing_card
            yield 'wait_card'

            for commands, index in player.valid_commands.items():
                if self.playing_card in commands and self.on_table.can_beplayed(player[index]):
                    to_do = player[index].action
                    break
                elif self.playing_card == 'draw':
                    to_do = ('draw', 1)
                    break
            else:
                await player.send('❌ You cannot send that card')
                self._pointer -= 1 if self.reverse else self.pointer + 1
                continue

            if to_do[0] == 'nothing':
                embed_turn

            # Wild Card
            if self.playing_card.startswith('wild'):
                embed_turn = await self.played_card(player, True, embed_turn)
                # Wild 4+
                if self.playing_card.endswith('plus'):
                    embed_turn = await self.draw_card_after_plus(embed_turn, 4)

            # Normal Card
            elif self.playing_card.startswith(list_on_table[0]) or self.playing_card.endswith(list_on_table[1]):
                embed_turn = await self.played_card(player, False, embed_turn)
                # Skip Card
                if self.playing_card.endswith('skip'):
                    self.pointer = await self.increment_pointer(self.pointer)
                    embed_turn.description += "\n{} turn is skipped".format(
                        self.order[self.pointer].user)
                # 2+ Card
                elif self.playing_card.endswith('plus'):
                    self.cards_to_draw += 2
                    embed_turn = await self.draw_card_after_plus(embed_turn, self.cards_to_draw)
                # Reverse Card
                elif self.playing_card.endswith('reverse'):
                    if len(self.order) == 2:
                        self.pointer = await self.increment_pointer(self.pointer)
                    else:
                        self.reverse = not self.reverse
                    embed_turn.description += "\nThe order has been reversed"

            # Draw a Card
            elif self.playing_card == 'draw':
                if drew_card:
                    await player.user.send("You can't draw two cards in one turn!")
                    continue
                if not self.drawing_deck:
                    self.drawing_deck = random.sample(
                        self.played_cards, k=len(self.played_cards))
                drawn_card = self.drawing_deck.pop(0)
                player.deck.append(drawn_card)
                if drawn_card.startswith(list_on_table[0]) or \
                        drawn_card.endswith(list_on_table[1]) or drawn_card.startswith("wild"):
                    await player.user.send("You can play the card you drew! In case you don't want to play user "
                                           "\"skip\"")
                    await player.user.send(self.deck_to_emoji(player, True))
                    drew_card = True
                    continue
                else:
                    embed_turn.description += "{} drew a card".format(
                        player.user)
                    embed_turn.set_thumbnail(url="https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck"
                                                 "/card%20draw.png")

            # Skip turn in case you got a card you can play
            elif self.playing_card == "skip" and drew_card and not self.settings["must_play"]:
                embed_turn.set_thumbnail(url="https://raw.githubusercontent.com/OrangSquid/UNO-Bot/master/deck"
                                             "/card%20draw.png")

            # Invalid Card
            else:
                await player.user.send("That card cannot be played!")
                continue

            await player.user.send(self.deck_to_emoji(player, True))
            # Check if the current player has been left without cards
            if not player.deck:
                self.order.remove(player)
                embed_turn.description += "\n{} has no cards! They are leaving the game!".format(
                    str(player.user))
            # Add one to the pointer (this after the possible player's removal to prevent bugs)
            self.pointer = await self.increment_pointer(self.pointer)
            embed_turn.description += "\nYour turn now **{}**\n".format(
                self.order[self.pointer].user)
            embed_turn.description += self.deck_to_emoji(
                self.order[self.pointer], False)
            if self.playing_card not in ['draw', 'skip']:
                embed_turn.color = COLOR_TO_DECIMAL[self.playing_card.split()[
                    0]]
            embed_turn.timestamp = datetime.datetime.now()
            drew_card = False
            await self.channel.send(embed=embed_turn)

        else:
            await self.channel.send("The game has ended!")

    async def played_card(self, player: Player, is_wild: bool, embed: discord.Embed()) -> discord.Embed:
        # Sets the card on the table and makes an embed to send
        player.deck.remove(self.playing_card)
        if is_wild:
            await player.user.send("Choose your color (red, yellow, green, blue)")
            await self.channel.send("Choose your color (red, yellow, green, blue)")
            # Waits for the message and self.color_change is also changed in the check function
            await self.bot.wait_for("message", check=self.check_wild_card_color)
            self.playing_card = "{} {}".format(
                self.color_change, self.playing_card)
            self.on_table = "{} wild".format(self.color_change)
            self.color_change = None
        else:
            self.on_table = self.playing_card
        embed.description += "{.user} played a {}".format(
            player, self.card_info[self.playing_card][0])
        embed.set_thumbnail(url=self.card_info[self.playing_card][2])
        self.played_cards.append(self.playing_card)
        return embed

    async def draw_card_after_plus(self, embed: discord.Embed(), cards_to_draw: int) -> discord.Embed:
        pointer_np = await self.increment_pointer(self.pointer)
        # Stacking definition
        if self.settings["stacking"]:
            for card in self.order[pointer_np].deck:
                if not card.startswith("wild") and card.endswith("plus"):
                    return embed
        for _ in range(cards_to_draw):
            if not self.drawing_deck:
                self.drawing_deck = random.sample(
                    self.played_cards, k=len(self.played_cards))
            self.order[pointer_np].deck.append(self.drawing_deck.pop(0))
        await self.order[pointer_np].user.send(self.deck_to_emoji(self.order[pointer_np], True))
        self.cards_to_draw = 0
        # Draw skip definition
        if self.settings["draw_skip"]:
            self.pointer = pointer_np
            embed.description += "\n{} drew {} and their turn is skipped".format(
                self.order[pointer_np].user, cards_to_draw)
        else:
            embed.description += "\n{} drew {}".format(
                self.order[pointer_np].user, cards_to_draw)
        return embed

    def check_playing_card(self, message: discord.Message) -> bool:
        content = message.content
        if ((message.author == self.waiting_for.user and (message.author.dm_channel == message.channel or
                                                          message.channel == self.channel)) and
                (content in self.waiting_for.deck or content == 'draw' or content == 'skip')) or self.stop:
            if self.cards_to_draw and (not content.startswith("wild") and content.endswith("plus")):
                self.playing_card = content
                return True
            elif not self.cards_to_draw:
                self.playing_card = content
                return True

    def check_wild_card_color(self, message: discord.Message) -> bool:
        if message.author == self.waiting_for.user and message.content in COLOR_TO_DECIMAL.keys():
            self.color_change = message.content
            return True
