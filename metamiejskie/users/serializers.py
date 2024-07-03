from allauth.account.models import EmailAddress
from dj_rest_auth.serializers import PasswordResetSerializer
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, PasswordField
from typing import Any, Dict, Optional, Type, TypeVar

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import AbstractBaseUser, update_last_login
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers
from rest_framework_simplejwt.settings import api_settings

from metamiejskie.users.models import User, DailyQuest, Quest, PatchNotes

from django.conf import settings

from metamiejskie.utils import DetailException


class CustomLoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = EmailAddress.objects.filter(user__username=attrs["username"]).first()
        if not email:
            raise DetailException("Email not found")
        if not email.verified:
            raise DetailException("Email is not verified")
        return super().validate(attrs)


class UserListSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["id", "username", "points"]


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = UserListSerializer.Meta.fields + [
            "coins",
            "exp",
            "exp_to_next_level",
            "level",
            "daily_coins_redeemed",
            "coins_lost_in_casino",
            "casino_wins",
            "casino_loses",
        ]


class DailyQuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyQuest
        fields = ["id", "created_at", "will_end_at", "quest", "user"]


class DailyQuestStartSerializer(serializers.ModelSerializer):
    time = serializers.SerializerMethodField()

    class Meta:
        model = DailyQuest
        fields = ["id", "created_at", "will_end_at", "redeemed", "quest", "time"]
        write_only_fields = ["quest"]
        read_only_fields = ["id", "created_at", "will_end_at", "redeemed", "time"]

    def get_time(self, obj) -> int:
        return obj.quest.duration.total_seconds()

    def validate(self, attrs):
        user = self.context["request"].user
        if user.level < attrs["quest"].level_required:
            raise DetailException("Hit level first")
        if user.has_daily_quest():
            raise DetailException("You already have a daily quest")
        attrs["user"] = user
        return super().validate(attrs)


class QuestSerializer(serializers.ModelSerializer):
    can_start = serializers.SerializerMethodField()

    def get_can_start(self, obj) -> bool:
        user = self.context["request"].user
        return user.level >= obj.level_required

    class Meta:
        model = Quest
        fields = ["id", "title", "description", "duration", "level_required", "can_start"]


class DailyQuestStatusSerializer(serializers.ModelSerializer):
    quest = QuestSerializer()
    total_time = serializers.SerializerMethodField()
    remaining_time = serializers.SerializerMethodField()
    finished = serializers.SerializerMethodField()

    def get_total_time(self, obj) -> int:
        return int(obj.quest.duration.total_seconds())

    def get_remaining_time(self, obj) -> int:
        remaining = (obj.will_end_at - timezone.now()).total_seconds()
        return int(remaining) if remaining > 0 else 0

    def get_finished(self, obj) -> bool:
        return timezone.now() > obj.will_end_at

    class Meta:
        model = DailyQuest
        fields = ["id", "quest", "total_time", "remaining_time", "finished"]


class PatchNotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatchNotes
        fields = ["id", "date", "version", "text"]
