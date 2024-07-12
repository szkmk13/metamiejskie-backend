from datetime import timedelta

from django.core.validators import MinValueValidator
from django.utils import timezone
from rest_framework import serializers

from metamiejskie.bets.models import Bet, Vote
from metamiejskie.meetings.models import Meeting, Attendance, Place
from metamiejskie.users.models import User
from metamiejskie.users.serializers import UserListSerializer
from metamiejskie.utils import DetailException


class BetsListSerializer(serializers.ModelSerializer):
    started_by = UserListSerializer()
    can_vote = serializers.SerializerMethodField()

    def get_can_vote(self, obj) -> bool:
        return not obj.votes.filter(user=self.context["request"].user).exists()

    class Meta:
        model = Bet
        fields = [
            "id",
            "started_by",
            "text",
            "total_votes",
            "can_vote",
            "label_1",
            "label_2",
            "ratio_1",
            "ratio_2",
            "created_at",
            "deadline",
            "rewards_granted",
        ]


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = "__all__"


class CreateBetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bet
        exclude = ["started_by", "rewards_granted"]

    def validate(self, attrs):
        attrs["started_by"] = self.context["request"].user
        if not attrs.get("deadline"):
            attrs["deadline"] = timezone.now() + timedelta(days=1)
        return super().validate(attrs)


class BetVoteSerializer(serializers.ModelSerializer):
    vote = serializers.ChoiceField(choices=Vote.Fields)

    class Meta:
        model = Vote
        fields = ["amount", "vote"]

    def validate(self, attrs):
        attrs["user"] = self.context["request"].user
        attrs["bet"] = self.context["bet"]
        if self.context["bet"].user_has_voted(attrs["user"]):
            raise DetailException("Already voted")
        attrs = super().validate(attrs)
        return attrs
