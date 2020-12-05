class Card:

    def __init__(self, card_dict):
        self.name = card_dict['name']
        self.emoji = card_dict['emoji']
        self.alias = card_dict['alias']
        self.image_url = card_dict['image_url']
    
    def __str__(self):
        return self.name

    def action(self):
        if self.name.startswith('**WILD'):
            if self.name.endswith('4+**'):
                return 'color_change', 4
            else:
                return 'color_change', 0
        elif self.name.endswith('SKIP**'):
            return 'skip', 0
        elif self.name.endswith('REVERSE**'):
            return 'reverse', 0
        elif self.name.endswith('2+**'):
            return 'plus', 2
        else:
            return 'nothing', 0
    
    def can_be_played(self, card):
        self_split = self.name.split()
        card_split = card.name.split()
        return card_split[0] in self_split[0] or card_split[1] in self_split[1] or card_split[0] == '**WILD'