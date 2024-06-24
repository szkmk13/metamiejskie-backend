import json

from rest_framework import serializers

from metamiejskie.bingo.models import Bingo, BingoField


class BingoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bingo
        fields = ["id", "order", "date", "completed"]


class BingoChangeFieldSerializer(serializers.Serializer):
    field_name = serializers.CharField()

    def validate(self, attrs):
        field_name = attrs.get("field_name")
        field_name = field_name.lower()
        if field_name not in BingoField.objects.values_list("name", flat=True):
            raise serializers.ValidationError("Field name is not valid")
        if self.context["bingo"].check_field(field_name):
            raise serializers.ValidationError("You got this field already")
        return attrs
