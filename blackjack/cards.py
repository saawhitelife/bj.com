import collections
from random import shuffle

# namedtuple for FrenchDeck card list
Card = collections.namedtuple('Card', ['rank', 'suit'])


class FrenchDeck:
    """
    Card deck
    """

    ranks = [str(n) for n in range(2, 11)] + list('JQKA')
    suits = 'spades diamonds clubs hearts'.split()

    def __init__(self):
        """

        :return:
        """

        self.cards = [Card(rank, suit) for suit in self.suits for rank in self.ranks]
        shuffle(self.cards)

    def __len__(self):
        """

        :return:
        """

        return len(self.cards)