from django.db import models as models
from cards import FrenchDeck
from djangotoolbox.fields import ListField
from uuid import uuid4
from django.core.validators import MinValueValidator

class Player(models.Model):
    """
    Players
    """

    # Player instance variables
    wallet_id = models.TextField(default=str(uuid4()), primary_key=True)
    wallet_balance = models.PositiveIntegerField(default=5000, validators=[MinValueValidator(1)])

class GameAction(models.Model):
    """ Game actions
    """

    # GameAction instance variables
    action_id = models.TextField(default=str(uuid4()), primary_key=True)
    action_time = models.DateTimeField(auto_now_add=True, auto_now=True)
    action_type = models.TextField()
    next_actions = models.TextField()
    player_hand = ListField()
    dealer_hand = ListField()
    bet = models.PositiveIntegerField(default=0, validators=[MinValueValidator(1)])
    player_points = models.PositiveSmallIntegerField(default=0)
    dealer_points = models.SmallIntegerField(default=0)
    player_blackjack = models.BooleanField(default=False)
    dealer_blackjack = models.BooleanField(default=False)
    player_bust = models.BooleanField(default=False)
    dealer_bust = models.BooleanField(default=False)
    game_push = models.BooleanField(default=False)
    player_win = models.BooleanField(default=False)
    dealer_win = models.BooleanField(default=False)
    end_game_action = models.BooleanField(default=False)
    player = models.ForeignKey(Player, related_name='player', on_delete=models.CASCADE)
    action_deck = ListField()
    player_action = models.TextField()

    def calculate_points(self, cards):
        """
        Calculate hand points
        :param cards: list list of namedtuple
        :return: int hand points
        """

        # Aggregate points
        points = 0

        for card in cards:
            if card[0] in 'JQK':
                points += 10
                continue
            if card[0] == 'A':
                if points > 10:
                    points += 1
                else:
                    points += 11
                continue
            else:
                points += int(card[0])
        return points

    def deal(self):
        """
        Deal game action
        :return: None
        """

        # Initialize the deck
        deck = FrenchDeck()
        self.action_deck = deck.cards

        # Set a game action
        self.action_type = 'deal'

        # Generate hands
        self.player_hand = [self.action_deck.pop() for i in range(2)]
        self.dealer_hand = [self.action_deck.pop() for i in range(2)]

        # Calculate points
        self.player_points = self.calculate_points(self.player_hand)
        self.dealer_points = self.calculate_points(self.dealer_hand)

        # Conditions

        # If a player has blackjack, we check if the dealer has it, in case both players have blackjack its a push
        if self.player_points == 21 and self.dealer_points == 21:
            self.end_game_action = True
            self.game_push = True
            self.dealer_blackjack = True
            self.player_blackjack = True
            self.next_actions = 'new'

        # If a player has blackjack and the dealer has less than 21 after deal (second card is revealed), player wins
        elif self.player_points == 21 and self.dealer_points < 21:
            self.end_game_action = True
            self.player_win = True
            self.player_blackjack = True
            self.next_actions = 'new'
            self.player.wallet_balance += self.bet * 1.5
            self.player.save()

        # If a player has less than 21 points and dealer has <= 21 points (second card is hidden)
        #  The player chooses to hit or stand
        elif self.player_points < 21 and self.dealer_points <= 21:
            self.next_actions = 'hit/stand'

    def hit(self):
        """
        Hit game action
        :return: None
        """

        # Setting action type
        self.action_type = 'hit'

        # One more card for the player
        self.player_hand.append(self.action_deck.pop())

        # Calculate points
        self.player_points = self.calculate_points(self.player_hand)

        # Conditions
        # If the player has 21 and after revealing second card the dealer has 21, dealer has blackjack
        if self.player_points == 21 and self.dealer_points == 21:
            self.end_game_action = True
            self.dealer_blackjack = True
            self.dealer_win = True
            self.player.wallet_balance -= self.bet
            self.player.save()
            self.next_actions = 'new'

        # Player bust
        elif self.player_points > 21:
            self.end_game_action = True
            self.player_bust = True
            self.dealer_win = True
            self.player.wallet_balance -= self.bet
            self.player.save()
            self.next_actions = 'new'

        # Player got under 21
        elif self.player_points < 21:
            self.next_actions = 'hit/stand'

        # Player got 21, the dealer has less then 21 (second card revealed), player wins
        elif self.player_points == 21 and self.dealer_points < 21:
            self.end_game_action = True
            self.player_win = True
            self.player.wallet_balance += self.bet
            self.player.save()
            self.next_actions = 'new'

    def stand(self):
        """
        Stand game action
        :return: none
        """

        # Setting action type
        self.action_type = 'stand'

        # Dealer blackjack after revealing the second card
        if self.dealer_points == 21:
            self.dealer_blackjack = True
            self.dealer_win = True
            self.end_game_action = True
            self.player.wallet_balance -= self.bet
            self.player.save()
            self.next_actions = 'new'

        # Player wins if dealer points greater than 17 and player points greater than dealer points
        elif self.dealer_points > 17 and self.player_points > self.dealer_points:
            self.player_win = True
            self.end_game_action = True
            self.player.wallet_balance += self.bet
            self.player.save()
            self.next_actions = 'new'

        # Dealer points greater than player ones after revealing the second card
        elif self.dealer_points > self.player_points:
            self.end_game_action = True
            self.dealer_win = True
            self.player.wallet_balance -= self.bet
            self.player.save()
            self.next_actions = 'new'

        # Cards for the dealer if total points <= 17 and dealer points are less or equal than player points
        elif self.dealer_points <= 17 and self.dealer_points <= self.player_points:

            # Pick cards until bust, 21, or win
            while self.dealer_points < 21:
                self.dealer_hand.append(self.action_deck.pop())
                self.dealer_points = self.calculate_points(self.dealer_hand)

                # Conditions
                # Dealer bust
                if self.dealer_points > 21:
                    self.end_game_action = True
                    self.dealer_bust = True
                    self.player_win = True
                    self.player.wallet_balance += self.bet
                    self.player.save()
                    self.next_actions = 'new'
                    break

                # Dealer got 21 and won
                elif self.dealer_points == 21:
                    self.end_game_action = True
                    self.dealer_win = True
                    self.player.wallet_balance -= self.bet
                    self.player.save()
                    self.next_actions = 'new'
                    break

                # Dealer points greater than player ones
                elif self.dealer_points > self.player_points:
                    self.end_game_action = True
                    self.dealer_win = True
                    self.player.wallet_balance -= self.bet
                    self.player.save()
                    self.next_actions = 'new'
                    break