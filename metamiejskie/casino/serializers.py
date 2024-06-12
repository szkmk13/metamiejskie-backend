from rest_framework import serializers, validators
from django.core.validators import MinValueValidator

from metamiejskie.casino.models import Game, Symbol


class SymbolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Symbol
        fields = "__all__"


class GameSerializer(serializers.ModelSerializer):
    symbols = SymbolSerializer(many=True)

    class Meta:
        model = Game
        fields = "__all__"


class GameSpinSerializer(serializers.ModelSerializer):
    bet_amount = serializers.IntegerField(write_only=True, validators=[MinValueValidator(1)])
    lines_chosen = serializers.IntegerField(default=1, write_only=True)

    class Meta:
        model = Game
        fields = ["bet_amount", "lines_chosen"]

    def validate(self, attrs):
        user = self.context["request"].user
        if attrs["bet_amount"] > user.coins:
            raise serializers.ValidationError("Insufficient kosa coins")
        return attrs


class SpinResultSerializer(serializers.Serializer):
    won = serializers.BooleanField(read_only=True, default=False)
    amount = serializers.IntegerField(read_only=True, default=0)
    result = serializers.ListSerializer(child=SymbolSerializer(many=True))

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        return rep
