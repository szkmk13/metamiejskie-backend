import itertools
from random import shuffle

from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from metamiejskie.casino.models import Game, HighCard
from metamiejskie.casino.serializers import (
    GameSerializer,
    GameSpinSerializer,
    HighCardResultSerializer,
    HighCardPlaySerializer,
)


# Create your views here.
@extend_schema(tags=["casino WORK IN PROGRESS"])
class CardGameViewSet(GenericViewSet):
    queryset = HighCard.objects.all()
    permission_classes = [IsAuthenticated]

    @action(detail=True)
    def play(self, request, pk=None):
        print(HighCard.objects.get(id=pk))
        card_game = HighCard.objects.get(id=pk)
        return Response(card_game.play())


@extend_schema(tags=["casino WORK IN PROGRESS"])
class CasinoViewSet(ListModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]

    CARD_VALUES = [2, 3, 4, 5, 6, 7, 8, 9, 10, "J", "Q", "K", "A"]
    CARD_SUITS = ["clubs", "hearts", "diamonds", "spades"]
    DECK = [f"{x}of{y}" for x, y in itertools.product(CARD_VALUES, CARD_SUITS)]

    def get_serializer_class(self):
        if self.action == "spin":
            return GameSpinSerializer
        return GameSerializer

    def get_queryset(self):
        return Game.objects.exclude(name__endswith="high card")

    @extend_schema(summary="Get list of possible games")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # @extend_schema(
    #     request=GameSpinSerializer,
    #     responses={200: SpinResultSerializer},
    #     summary="""Provide id of the game and play it""",
    # )
    # @action(methods=["post"], detail=True)
    # def spin(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     obj = self.get_object()
    #     result = obj.play()
    #     result = SpinResultSerializer(obj.play(self.request.user, serializer.validated_data["lines_chosen"]))
    #     print(obj)
    #     return Response(result.data)

    @extend_schema(
        request=HighCardPlaySerializer,
        responses={200: HighCardResultSerializer},
        summary="""Place bet if next card will be higher lower or same""",
    )
    @action(methods=["post"], detail=False)
    def play_high_card(self, request, *args, **kwargs):
        serializer = HighCardPlaySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        game_object, _ = HighCard.objects.get_or_create(user=request.user, name=f"{request.user.id}high card")
        bet_amount = serializer.validated_data["bet_amount"]
        shuffle(self.DECK)
        next_card = self.DECK[0]

        if bet_amount == 0:
            card_value, card_suit = next_card.split("of")
            data = {"bet_amount": bet_amount, "card_suit": card_suit, "card_value": card_value, "demo_play": True}
            game_object.last_card = next_card
            game_object.save()
            return Response(HighCardResultSerializer(data).data)

        next_card_value, next_card_suit = next_card.split("of")
        data = {
            "bet_amount": bet_amount,
            "card_suit": next_card_suit,
            "card_value": next_card_value,
            "previous_card_value": game_object.last_card.split("of")[0],
            "next_card_value": next_card_value,
            "bet": serializer.validated_data["bet"],
        }

        serializer = HighCardResultSerializer(data=data, context={"user": request.user, "game_object": game_object})
        serializer.is_valid(raise_exception=True)
        game_object.last_card = next_card
        game_object.save()
        return Response(serializer.data)
