from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator, MinLengthValidator
from django.utils import timezone
from rest_framework import serializers, permissions, viewsets
from rest_framework.exceptions import APIException

from metamiejskie.meetings.models import Meeting, Attendance, Place
from metamiejskie.users.models import User


class TrojmiejskiException(APIException):
    status_code = 400
    default_detail = f"Żeby spotkanie się liczyło musi na nim być conajmniej {Meeting.MIN_ATTENDANCE} trójmiejskich"


class DateException(APIException):
    status_code = 400
    default_detail = "error"
    default_code = ""


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ["id", "name", "used_in_meetings"]
        read_only_fields = ["name"]


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = "__all__"


class UserMeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class UserAttendanceSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()

    def get_id(self, attendance):
        return attendance.user.id

    def get_username(self, attendance):
        return attendance.user.username

    class Meta:
        model = Attendance
        fields = ["id", "username", "drinking"]


class MeetingAddSerializer(serializers.ModelSerializer):
    participants = serializers.ListSerializer(
        child=serializers.PrimaryKeyRelatedField(queryset=User.objects.all()),
        write_only=True,
        help_text="List of ID's of users who participate in meeting",
    )
    who_drank = serializers.ListSerializer(
        child=serializers.PrimaryKeyRelatedField(queryset=User.objects.all()),
        write_only=True,
        help_text="default is everyone",
        required=False,
    )
    place = PlaceSerializer(read_only=True)
    users = UserMeetingSerializer(many=True, read_only=True)
    place_name = serializers.CharField(help_text="name of the place for example: Toruń", write_only=True, required=True)
    date = serializers.DateField(required=False, help_text="defaults to today")

    class Meta:
        model = Meeting
        fields = ["id", "participants", "who_drank", "place_name", "date", "place", "users", "pizza", "casino"]
        required_fields = ["place", "participants"]
        read_only_fields = ["users"]

    def create(self, validated_data):
        participants = validated_data.pop("participants")
        who_drank = validated_data.get("who_drank") or []
        if who_drank:
            validated_data.pop("who_drank")
        meeting = Meeting.objects.create(**validated_data)
        for user in participants:
            drinking = user.id in who_drank
            attendance = Attendance(meeting=meeting, user=user, drinking=drinking)
            if self.context["request"].user == user:
                attendance.confirmed = True
            attendance.save()
        return meeting

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if len(attrs["participants"]) < Meeting.MIN_ATTENDANCE:
            raise serializers.ValidationError("There must be at least 3 participants.")
        place_string = attrs.pop("place_name").strip().replace("_", " ").replace("-", " ")
        place = Place.objects.filter(name__iexact=place_string).first()
        if place:
            attrs["place"] = place
        else:
            attrs["place"] = Place.objects.create(name=place_string)
        if not attrs.get("date"):
            attrs["date"] = timezone.now().date()
        return attrs


class MeetingListSerializer(serializers.ModelSerializer):
    users = serializers.SerializerMethodField()
    place = PlaceSerializer()

    def get_users(self, obj) -> UserAttendanceSerializer(many=True):
        return UserAttendanceSerializer(obj.attendance_set, many=True).data

    class Meta:
        model = Meeting
        fields = ["id", "date", "is_confirmed_by_users", "place", "casino", "pizza", "users"]
