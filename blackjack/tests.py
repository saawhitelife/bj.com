"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from rest_framework.test import APIRequestFactory, APIClient
from django.contrib.auth.models import User
from django.test import TestCase, Client
from .import cards
from .models import Player, GameAction
import json


class ModelTest(TestCase):
    def test_player_creation(self):
        """
        Tests whether players are being created properly
        """
        player = Player()
        self.assertEqual(player.wallet_balance, 5000)
        self.assertIsNotNone(player.wallet_id)

    def test_game_action_creation(self):
        """
        Tests whether gameactions are being created properly
        """

        player = Player()
        action = GameAction(player=player, bet=50)
        self.assertTrue(action)
        self.assertEqual(action.next_actions, '')

    def test_deal_game_action(self):
        """
        Test whether we can invoke deal on gameaction
        """

        player = Player()
        action = GameAction(player=player, bet=50)
        action.deal()
        self.assertEqual(action.action_type, 'deal')
        self.assertIsNotNone(action.player_hand)
        self.assertIsNotNone(action.dealer_hand)
        self.assertIsNotNone(action.player_points)
        self.assertIsNotNone(action.dealer_points)
        self.assertIsNotNone(action.next_actions)

    def test_blackjack_on_deal_action(self):
        """
        Test if we can get blackjack on deal
        """

        while True:
            player = Player()
            action = GameAction(player=player, bet=50)
            action.deal()
            if action.player_points == 21 and action.dealer_points < 21:
                break
        self.assertTrue(action.player_blackjack)
        self.assertEqual(len(action.player_hand), 2)
        self.assertEqual(len(action.action_deck), 48)
        self.assertTrue(action.player_win)
        self.assertEqual(action.player.wallet_balance, 5075)
        self.assertTrue(action.end_game_action)
        self.assertEqual(action.next_actions, 'new')

    def test_push_on_deal(self):
        """
        Test push with two blackjacks on deal
        """

        while True:
            player = Player()
            action = GameAction(player=player, bet=50)
            action.deal()
            if action.player_points == 21 and action.dealer_points == 21:
                break
        self.assertTrue(action.player_blackjack)
        self.assertTrue(action.dealer_blackjack)
        self.assertTrue(action.game_push)
        self.assertEqual(len(action.player_hand), 2)
        self.assertEqual(len(action.dealer_hand), 2)
        self.assertEqual(len(action.action_deck), 48)
        self.assertFalse(action.player_win)
        self.assertEqual(action.player.wallet_balance, 5000)
        self.assertTrue(action.end_game_action)
        self.assertEqual(action.next_actions, 'new')

    def test_hidden_card_on_deal(self):
        """
        Test if blackjack doesn't happen on deal when dealer has 21
        """

        while True:
            player = Player()
            action = GameAction(player=player, bet=50)
            action.deal()
            if action.player_points < 21 and action.dealer_points == 21:
                break
        self.assertFalse(action.dealer_blackjack)
        self.assertEqual(len(action.player_hand), 2)
        self.assertEqual(len(action.dealer_hand), 2)
        self.assertEqual(action.player.wallet_balance, 5000)
        self.assertFalse(action.end_game_action)
        self.assertEqual(action.next_actions, 'hit/stand')


class CardTest(TestCase):
    """
    Test our card deck :D
    """

    def test_card_deck_length(self):
        """
        Simple test
        """

        deck = cards.FrenchDeck()
        carddeck = deck.cards
        self.assertEqual(len(carddeck), 52)

    def test_card_deck_popping(self):
        """
        Pop deck
        """

        deck = cards.FrenchDeck()
        carddeck = deck.cards
        for i in range(5):
            carddeck.pop()
        self.assertEqual(len(carddeck), 47)


class ApiTest(TestCase):
    """
    Test our api
    """

    def test_root_view_for_non_authenticated_user(self):
        """
        Request without credentials
        """

        client = Client()
        response = client.get("/")
        self.assertJSONEqual(response.content, {"detail":"Authentication credentials were not provided."})

    def test_user_authentication(self):
        """
        User auth test
        """

        test_superuser = User.objects.create_superuser(username="vagrant", password="vagrant", email="")
        test_superuser.save()
        client = Client()
        self.assertTrue(client.login(username="vagrant", password="vagrant"))

    def test_root_view_for_authenticated_user(self):
        """
        Request root with credentials
        """

        test_superuser = User.objects.create_superuser(username="vagrant", password="vagrant", email="")
        test_superuser.save()
        client = Client()
        client.login(username="vagrant", password="vagrant")
        response = client.get("/")
        self.assertJSONEqual(response.content, {"gameactions":"http://testserver/blackjack/gameactions/","players":"http://testserver/players/"})

    def test_default_player_creation(self):
        """
        Test player creation through post
        """

        test_superuser = User.objects.create_superuser(username="vagrant", password="vagrant", email="")
        test_superuser.save()
        client = Client()
        client.login(username="vagrant", password="vagrant")
        response = client.post("/players/", data={})
        self.assertEqual(response.data['wallet_balance'], 5000)
        self.assertIsNotNone(response.data['wallet_id'])

    def test_player_creation_with_negative_wallet_value(self):
        """
        Test player creation through post with a negative wallet balance
        """

        test_superuser = User.objects.create_superuser(username="vagrant", password="vagrant", email="")
        test_superuser.save()
        client = Client()
        client.login(username="vagrant", password="vagrant")
        response = client.post("/players/", data={"wallet_balance":"-50"})
        self.assertJSONEqual(response.content, {"wallet_balance":["Ensure this value is greater than or equal to 1."]})

    def test_default_game_action_creation(self):
        """
        Test gameaction creation through post
        """

        test_superuser = User.objects.create_superuser(username="vagrant", password="vagrant", email="")
        test_superuser.save()
        client = Client()
        client.login(username="vagrant", password="vagrant")
        player = Player()
        player.save()
        response = client.post("/blackjack/gameactions/", data={"player": str(player.wallet_id), "bet": "50"})
        self.assertIsNotNone(response.data["action_id"])
        self.assertIsNotNone(response.data["bet"])
        self.assertIsNotNone(response.data["action_time"])

    def test_game_action_creation_with_negative_bet(self):
        """
        Same as previous but negative bet value
        """

        test_superuser = User.objects.create_superuser(username="vagrant", password="vagrant", email="")
        test_superuser.save()
        client = Client()
        client.login(username="vagrant", password="vagrant")
        player = Player()
        player.save()
        response = client.post("/blackjack/gameactions/", data={"player": str(player.wallet_id), "bet": "-50"})
        self.assertJSONEqual(response.content, {"bet":["Ensure this value is greater than or equal to 1."]})

    def test_deal_game_action(self):
        """
        Test deal gameaction
        """

        test_superuser = User.objects.create_superuser(username="vagrant", password="vagrant", email="")
        test_superuser.save()
        client = APIClient()
        client.login(username="vagrant", password="vagrant")
        player = Player()
        player.save()

        # Create game action
        wid = str(player.wallet_id)
        post_response = client.post("/blackjack/gameactions/", {"player": wid, "bet": "50"})
        aid = str(post_response.data["action_id"])
        at = str(post_response.data["action_time"])

        # Check whether we managed to create a gameaction
        self.assertIsNotNone(at)
        self.assertIsNotNone(aid)

        # Deal patch
        patch_response = client.patch("/blackjack/gameactions/"+aid+"/", {"player_action":"deal"}, format="json")

        # Assertion
        self.assertEqual(patch_response.data["action_type"], "deal")
        self.assertIsNotNone(patch_response.data["dealer_hand"])
        self.assertIsNotNone(patch_response.data["next_actions"])