from allauth.account.models import EmailAddress
from dj_rest_auth.serializers import PasswordResetSerializer
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, PasswordField
from typing import Any, Dict, Optional, Type, TypeVar

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import AbstractBaseUser, update_last_login
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.settings import api_settings

from metamiejskie.users.models import User, DailyQuest, Quest

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


class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["id", "username", "points", "coins", "exp", "exp_to_next_level", "level", "daily_coins_redeemed"]


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
            raise serializers.ValidationError("Hit level first")
        if user.has_daily_quest():
            raise serializers.ValidationError("You already have a daily quest")
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
