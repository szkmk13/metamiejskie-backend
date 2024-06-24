from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator, MinLengthValidator
from rest_framework import serializers, permissions, viewsets
from rest_framework.exceptions import APIException

from metamiejskie.meetings.models import Meeting, Attendance
from metamiejskie.users.models import User


class TrojmiejskiException(APIException):
    status_code = 400
    default_detail = f"Żeby spotkanie się liczyło musi na nim być conajmniej {Meeting.MIN_ATTENDANCE} trójmiejskich"


class DateException(APIException):
    status_code = 400
    default_detail = "error"
    default_code = ""


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = "__all__"


class MeetingAddSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    who_drank = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, write_only=True, required=False
    )

    class Meta:
        model = Meeting
        fields = "__all__"

    def create(self, validated_data):
        participants_data = validated_data.pop("participants")
        who_drank = validated_data.pop("who_drank")
        meeting = Meeting.objects.create(**validated_data)
        for participant_data in participants_data:
            drinking = participant_data.user.id in who_drank
            if User.objects.get(user=self.context["request"].user) == participant_data:
                Attendance.objects.create(meeting=meeting, user=participant_data, confirmed=True, drinking=drinking)
            else:
                Attendance.objects.create(meeting=meeting, user=participant_data, drinking=drinking)
        return meeting

    def validate(self, attrs):
        participants = attrs.get("participants", [])
        if len(participants) < Meeting.MIN_ATTENDANCE:
            raise serializers.ValidationError("There must be at least 3 participants.")
        if attrs.get("place") == "OTHER" and attrs.get("other_place") in (None, ""):
            raise serializers.ValidationError("Please enter place")
        return attrs


class MeetingListSerializer(serializers.ModelSerializer):
    participants = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    confirmed = serializers.SerializerMethodField()

    class Meta:
        model = Meeting
        fields = "__all__"

    def get_participants(self, obj):
        return [user.get_full_name() for user in obj.participants.all()]

    def get_date(self, obj):
        return obj.date

    def get_confirmed(self, obj):
        return obj.is_confirmed_by_users()


class ParticipantSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        return obj.user.get_full_name()

    class Meta:
        model = Attendance
        fields = ["user", "drinking"]


class MeetingDetailSerializer(serializers.ModelSerializer):
    participants = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()

    class Meta:
        model = Meeting
        fields = "__all__"

    def get_date(self, obj):
        return obj.date

    def get_participants(self, obj):
        participants = Attendance.objects.filter(meeting=obj)
        serializer = ParticipantSerializer(participants, many=True)
        return serializer.data
