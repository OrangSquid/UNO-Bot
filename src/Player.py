class Player:

    def __init__(self, user) -> None:
        self.deck = []
        self.valid_commands = {['draw']: None}
        self.user = user
        self.avatar_url = str(user.avatar_url)

    def __len__(self) -> int:
        return len(self.deck)
    
    def __str__(self) -> str:
        return str(self.user)
    
    def __getitem__(self, index):
        return self.deck[index]
    
    def draw(self, cards):
        for card, count in enumerate(cards):
            self.deck.append(card)
            self.valid_commands[card.alias] = count
    
    def mention(self):
        return self.user.mention
    
    def send(self, message):
        return self.user.send(message)
    
    def play_card(self, index):
        pass

    def deck_emoji(self) -> str:
        if not self.deck:
            return self.send('Your deck is empty')
        to_send = ''
        for card in self.deck:
            to_send += card.emoji
        return self.send(to_send)
    
    def deck_back(self) -> str:
        return '<:back:746444081424760943>' * len(self)