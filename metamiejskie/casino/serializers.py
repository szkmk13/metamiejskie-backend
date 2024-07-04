from rest_framework.serializers import *
from django.core.validators import MinValueValidator

from metamiejskie.casino.models import Game, Symbol, Spin, GAMES
from metamiejskie.utils import DetailException


class SymbolSerializer(ModelSerializer):
    class Meta:
        model = Symbol
        fields = "__all__"


class GameSerializer(ModelSerializer):
    symbols = SymbolSerializer(many=True)

    class Meta:
        model = Game
        fields = "__all__"


class GameSpinSerializer(ModelSerializer):
    bet_amount = IntegerField(write_only=True, validators=[MinValueValidator(0)])
    lines_chosen = IntegerField(default=1, write_only=True)

    class Meta:
        model = Game
        fields = ["bet_amount", "lines_chosen"]

    def validate(self, attrs):
        user = self.context["request"].user
        if attrs["bet_amount"] > user.coins:
            raise DetailException("Insufficient coins")
        return attrs


class HighCardPlaySerializer(Serializer):
    bet_amount = IntegerField(write_only=True, validators=[MinValueValidator(0)])
    bet = ChoiceField(choices=["high", "low", "equal"])


class HighCardResultSerializer(Serializer):
    demo_play = BooleanField(default=False)
    card_value = CharField()
    card_suit = CharField()
    bet_amount = IntegerField()
    has_won = BooleanField(default=False)
    reward = IntegerField(default=0)

    next_card_value = CharField(write_only=True)
    previous_card_value = CharField(write_only=True)
    bet = CharField(write_only=True)

    FACES_VALUES = {"J": 11, "Q": 12, "K": 13, "A": 14}
    HIGH_LOW_MULTIPLIER = 1.4
    EQUAL_MULTIPLIER = 6

    class Meta:
        fields = "__all__"

    def validate(self, attrs):
        previous_card_value = (
            self.FACES_VALUES.get(attrs["previous_card_value"])
            if attrs["previous_card_value"].isalpha()
            else int(attrs["previous_card_value"])
        )
        next_card_value = (
            self.FACES_VALUES.get(attrs["next_card_value"])
            if attrs["next_card_value"].isalpha()
            else int(attrs["next_card_value"])
        )
        bet_amount = attrs.get("bet_amount")
        bet = attrs.get("bet")
        user = self.context["user"]
        if user.coins < bet_amount:
            raise DetailException("Insufficient coins")
        user.coins -= bet_amount
        if bet == "high":
            if next_card_value > previous_card_value:
                user.coins += self.HIGH_LOW_MULTIPLIER * bet_amount
                attrs["has_won"] = True
                attrs["reward"] = self.HIGH_LOW_MULTIPLIER * bet_amount
        elif bet == "low":
            if next_card_value < previous_card_value:
                user.coins += self.HIGH_LOW_MULTIPLIER * bet_amount
                attrs["has_won"] = True
                attrs["reward"] = self.HIGH_LOW_MULTIPLIER * bet_amount
        elif bet == "equal":
            if next_card_value == previous_card_value:
                user.coins += self.EQUAL_MULTIPLIER * bet_amount
                attrs["has_won"] = True
                attrs["reward"] = self.EQUAL_MULTIPLIER * bet_amount
        spin = Spin(game=GAMES.HIGH_CARD, user=user, has_won=attrs["has_won"])
        if attrs["has_won"]:
            spin.amount = attrs["reward"]
        else:
            spin.amount = bet_amount
        user.save(update_fields=["coins"])
        spin.save()
        return attrs


class SpinResultSerializer(Serializer):
    won = BooleanField(read_only=True, default=False)
    amount = IntegerField(read_only=True, default=0)
    result: ListSerializer[SymbolSerializer] = ListSerializer(child=SymbolSerializer(many=True))

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        return rep
