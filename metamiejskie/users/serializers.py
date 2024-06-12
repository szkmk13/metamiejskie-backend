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


class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["id", "username", "kosa_points", "kosa_coins", "exp", "level", "daily_coins_redeemed"]


class DailyQuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyQuest
        fields = ["id", "created_at", "will_end_at", "quest", "user"]


class DailyQuestStartSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyQuest
        fields = ["id", "created_at", "will_end_at", "redeemed", "quest"]
        write_only_fields = ["quest"]
        read_only_fields = ["id", "created_at", "will_end_at", "redeemed"]

    def validate(self, attrs):
        user = self.context["request"].user
        if user.has_daily_quest():
            raise serializers.ValidationError("You already have a daily quest")
        attrs["user"] = user
        return super().validate(attrs)


class QuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quest
        fields = ["id", "title", "description", "duration", "level_required"]
