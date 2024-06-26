from rest_framework.serializers import *
from django.core.validators import MinValueValidator

from metamiejskie.casino.models import Game, Symbol
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
    bet_amount = IntegerField(write_only=True, validators=[MinValueValidator(1)])
    lines_chosen = IntegerField(default=1, write_only=True)

    class Meta:
        model = Game
        fields = ["bet_amount", "lines_chosen"]

    def validate(self, attrs):
        user = self.context["request"].user
        if attrs["bet_amount"] > user.coins:
            raise DetailException("Insufficient coins")
        return attrs


class SpinResultSerializer(Serializer):
    won = BooleanField(read_only=True, default=False)
    amount = IntegerField(read_only=True, default=0)
    result: ListSerializer[SymbolSerializer] = ListSerializer(child=SymbolSerializer(many=True))

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        return rep
