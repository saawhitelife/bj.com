from blackjack.models import Player, GameAction
from rest_framework import serializers


class PlayerSerializer(serializers.ModelSerializer):
    """
    Auto-serialize Player model fields
    """

    class Meta:
        model = Player
        fields = ('wallet_id', 'wallet_balance')


class GameActionSerializer(serializers.ModelSerializer):
    """
    Serialize GameAction model fields
    """
    player_action = serializers.CharField(required=False, allow_blank=True)
    dealer_hand = serializers.ListField(required=False, allow_empty=True)
    next_actions = serializers.CharField(required=False, allow_blank=True)
    player_hand = serializers.ListField(required=False, allow_empty=True)
    player_points = serializers.IntegerField(required=False, allow_null=True)
    dealer_points = serializers.IntegerField(required=False, allow_null=True)
    action_type = serializers.CharField(required=False, allow_blank=True)
    action_id = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = GameAction
        fields = ('action_type', 'action_time', 'action_id', 'player_hand', 'dealer_hand', 'dealer_points',
                  'player_points', 'end_game_action', 'player_blackjack', 'dealer_blackjack', 'player_bust',
                  'dealer_bust', 'player_win', 'dealer_win', 'game_push', 'next_actions', 'bet', 'player_action',
                  'player')