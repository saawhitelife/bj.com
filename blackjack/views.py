from blackjack.models import Player, GameAction
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response
from blackjack.serializers import PlayerSerializer, GameActionSerializer
from django.core.exceptions import ValidationError

@api_view(['GET'])
def api_root(request, format=None):
    """
    REST index page
    """

    return Response({
        'players': reverse('player-list', request=request),
        'gameactions': reverse('gameaction-list', request=request),
    })


class PlayerList(generics.ListCreateAPIView):
    """
    List Player instances
    """

    # Override defaults
    lookup_field = 'wallet_id'
    queryset = Player.objects.all()
    model = Player
    serializer_class = PlayerSerializer


class PlayerDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Player API
    """

    lookup_field = 'wallet_id'
    model = Player
    serializer_class = PlayerSerializer

    def get(self, request, pk, format=None):
        """

        :param request:
        :param pk:
        :param format:
        :return:
        """

        player = Player.objects.get(wallet_id=pk)
        serializer = self.serializer_class(player)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        """

        :param request:
        :param pk:
        :param format:
        :return:
        """

        player = Player.objects.get(wallet_id=request.data.get('wallet_id'))
        player.wallet_balance = request.data.get('wallet_balance')
        try:
            player.full_clean()
        except ValidationError as e:
            return Response(e.message_dict)
        else:
            player.save()
            serializer = self.serializer_class(player)
            return Response(serializer.data)

    def post(self, request, format=None):
        """

        :param request:
        :param format:
        :return:
        """

        player = Player.objects.create(wallet_balance=request.data.get('wallet_balance'))
        player.save()
        serializer = self.serializer_class(player)
        return Response(serializer.data)


class GameActionList(generics.ListCreateAPIView):
    """
    List GameAction instances
    """

    # Override defaults
    lookup_field = 'action_id'
    queryset = GameAction.objects.all()
    model = GameAction
    serializer_class = GameActionSerializer


class GameActionDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    GameAction API
    """

    # Override defaults
    model = GameAction
    serializer_class = GameActionSerializer

    def get(self, request, pk, format=None):
        """

        :param request:
        :param pk:
        :param format:
        :return:
        """

        action = GameAction.objects.get(action_id=pk)
        serializer = self.serializer_class(action)
        return Response(serializer.data)

    def post(self, request, format=None):
        """

        :param request:
        :param format:
        :return:
        """

        if request.data.get('player') and request.data.get('bet'):
            player = Player.objects.get(wallet_id=request.data.get('player'))
            action = GameAction(player=player, bet=request.data.get('bet'))
            try:
                action.full_clean()
            except ValidationError as e:
                return Response(e.message_dict)
            else:
                action.save()
                serializer = self.serializer_class(action)
                return Response(serializer.data)

        else:
            return Response(data=None, status=400)

    def patch(self, request, pk, format=None):
        """

        :param request:
        :param pk:
        :param format:
        :return:
        """

        action = GameAction.objects.get(action_id=pk)

        if action.end_game_action:
            serializer = self.serializer_class(action)
            return Response(serializer.data, status=304)

        # Conditions
        elif action.next_actions == 'hit/stand' and request.data.get('player_action') == 'hit':
            action.player_action = 'hit'
            action.hit()
            action.save()
            serializer = self.serializer_class(action)
            return Response(serializer.data)

        elif action.next_actions == 'hit/stand' and request.data.get('player_action') == 'stand':
            action.player_action = 'stand'
            action.stand()
            action.save()
            serializer = self.serializer_class(action)
            return Response(serializer.data)

        elif action.next_actions == '' and request.data.get('player_action') == 'deal':
            action.player_action = 'deal'
            action.deal()
            action.save()
            serializer = self.serializer_class(action)
            return Response(serializer.data)

        else:
            return Response(data=None, status=400)